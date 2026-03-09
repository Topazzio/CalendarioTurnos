from email import message

from fastapi import FastAPI, HTTPException
from datetime import date, timedelta
from backend.availability import build_week_availability
from backend.google_calendar import create_event, is_slot_available
from backend.models import BookingRequest
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from zoneinfo import ZoneInfo
from backend.locks import create_lock, is_locked, remove_lock
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
import urllib.parse
import time
import os

calendar_cache = {}
CACHE_DURATION = 30  # segundos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
BUSINESS_PHONE = os.getenv("BUSINESS_PHONE")

if not BUSINESS_PHONE:
    raise ValueError("BUSINESS_PHONE environment variable not set")

app = FastAPI()

SCOPES = ["https://www.googleapis.com/auth/calendar"]

TZ = ZoneInfo("America/Argentina/Cordoba")

# CORS (seguridad)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/availability")
def availability():
    return {"message": "slots here"}


@app.get("/calendar")
def calendar():
    return FileResponse("templates/calendar.html")

@app.get("/calendars")
def list_calendars():
    from google_calendar import get_calendar_service

    service = get_calendar_service()

    calendars = service.calendarList().list().execute()

    return calendars

@app.get("/week-availability")
def week_availability(week_offset: int = Query(0)):

    cache_key = f"week_{week_offset}"
    now = time.time()

    # 🔵 Revisar cache
    if cache_key in calendar_cache:
        cached = calendar_cache[cache_key]

        if now - cached["timestamp"] < CACHE_DURATION:
            return cached["data"]

    today = date.today()
    monday = today - timedelta(days=today.weekday())
    selected_week = monday + timedelta(weeks=week_offset)


    data = {
        "week_start": selected_week,
        "days": build_week_availability(selected_week)
    }

    # 💾 Guardar en cache
    calendar_cache[cache_key] = {
        "timestamp": now,
        "data": data
    }

    return data
from fastapi.responses import HTMLResponse

@app.post("/book")  
def book_turno(data: BookingRequest):

    now = datetime.now(TZ)

    # ✅ convertir timezone correctamente
    start_time = data.start_time.replace(tzinfo=None)
    start_time = start_time.replace(tzinfo=TZ)

    # ✅ validar pasado
    if start_time <= now:
        raise HTTPException(400, "Horario pasado")

    # ✅ calcular duración
    end_time = start_time + timedelta(hours=1)

    start_iso = start_time.isoformat()
    end_iso = end_time.isoformat()

    # ✅ lock temporal (tipo cine)
    if is_locked(start_iso):
        raise HTTPException(409, "Turno reservado temporalmente")

    # ✅ chequeo real contra Google Calendar
    if not is_slot_available(start_iso, end_iso):
        raise HTTPException(
            409,
            "El turno acaba de ser reservado por otra persona"
        )

    # ✅ crear evento
    event = create_event(
        summary=f"Turno de {data.name}, {data.phone}, {data.material}, {data.pago}",
        start_time=start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        end_time=end_time.strftime("%Y-%m-%dT%H:%M:%S")
    )

    # ✅ liberar lock
    remove_lock(start_iso)

    # 🟢 MENSAJE WHATSAPP
    message = f"""
¡Hola! Te paso el resumen de mi turno

Teléfono: {data.phone}

Fecha: {start_time.strftime("%d/%m/%Y")}
Hora: {start_time.strftime("%H:%M")}

Auto: {data.auto} ({data.anio})
Material: {data.material}

Dirección:
https://maps.app.goo.gl/8qJapg3rEW255nYw5

Nos vemos!
"""

    encoded_message = urllib.parse.quote(message)

    whatsapp_link = f"https://wa.me/{BUSINESS_PHONE}?text={encoded_message}"
    
    return {
    "status": "confirmed",
    "event_id": event["id"],
    "whatsapp_link": whatsapp_link
    }

@app.post("/hold")
def hold_turn(data: BookingRequest):

    start = data.start_time.replace(tzinfo=None)
    start = start.replace(tzinfo=TZ).isoformat()

    if is_locked(start):
        raise HTTPException(409, "Turno en proceso de reserva")

    create_lock(start)

    return {"status": "locked", "expires_in": "5 minutes"}

#SIEMPRE AL FINAL
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
