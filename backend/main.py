from fastapi import FastAPI, HTTPException
from datetime import date, timedelta
from backend.availability import build_week_availability
from google_calendar import create_event, is_slot_available
from backend.models import BookingRequest
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from zoneinfo import ZoneInfo
from backend.locks import create_lock, is_locked, remove_lock
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time

calendar_cache = {}
CACHE_DURATION = 30  # segundos

app = FastAPI()

SCOPES = ["https://www.googleapis.com/auth/calendar"]

TZ = ZoneInfo("America/Argentina/Cordoba")


app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")

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

# Servir frontend
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
@app.get("/")
def home():
    return FileResponse("../frontend/index.html")

@app.get("/accesorios")
def accesorios():
    return FileResponse("../frontend/accesorios.html")

@app.get("/faq")
def faq():
    return FileResponse("../frontend/FAQ.html")

@app.get("/turno")
def turnos():
    return FileResponse("../frontend/turno.html")

@app.get("/auth")
def auth():

    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json",
        SCOPES
    )

    # 👇 ESTA LÍNEA ES LA CLAVE
    creds = flow.run_local_server(
        port=8080,
        access_type="offline",
        prompt="consent"
    )

    with open("token.json", "w") as token:
        token.write(creds.to_json())

    return {"status": "Google Calendar conectado correctamente ✅"}

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
def week_availability(week_offset: int = 0):

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

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>Servidor de Turnos funcionando ✅</h1>
    <p><a href="/auth">Conectar Google Calendar</a></p>
    """



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
        summary=f"Turno {data.name}, {data.phone}",
        start_time=start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        end_time=end_time.strftime("%Y-%m-%dT%H:%M:%S")
    )

    # ✅ liberar lock
    remove_lock(start_iso)

    return {"status": "confirmed", "event_id": event["id"]}

@app.post("/hold")
def hold_turn(data: BookingRequest):

    start = data.start_time.replace(tzinfo=None)
    start = start.replace(tzinfo=TZ).isoformat()

    if is_locked(start):
        raise HTTPException(409, "Turno en proceso de reserva")

    create_lock(start)

    return {"status": "locked", "expires_in": "5 minutes"}