from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os
from zoneinfo import ZoneInfo


SCOPES = ['https://www.googleapis.com/auth/calendar']

CALENDAR_ID = "e8792ead27291cf084c84035f6def39542154d65524de10263172dbb7e996b18@group.calendar.google.com"
TIMEZONE = "America/Argentina/Cordoba"

def get_calendar_service():

    creds = None

    # ✅ usar token existente
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # ✅ si no existe o expiró → login
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # guardar token
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_busy_times(date):

    service = get_calendar_service()

    tz = ZoneInfo(TIMEZONE)

    # inicio del día en hora argentina
    start_local = datetime.combine(date, datetime.min.time(), tz)
    end_local = start_local + timedelta(days=1)

    body = {
        "timeMin": start_local.isoformat(),
        "timeMax": end_local.isoformat(),
        "items": [{"id": CALENDAR_ID}]
    }

    result = service.freebusy().query(body=body).execute()

    return result["calendars"][CALENDAR_ID]["busy"]


def create_event(summary, start_time, end_time):

    service = get_calendar_service()

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time,
            "timeZone": TIMEZONE
        },
        "end": {
            "dateTime": end_time,
            "timeZone": TIMEZONE
        },
    }

    return service.events().insert(
        calendarId=CALENDAR_ID,
        body=event
    ).execute()

def is_slot_available(start_time, end_time):

    service = get_calendar_service()

    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "items": [{"id": CALENDAR_ID}]
    }

    result = service.freebusy().query(body=body).execute()

    busy = result["calendars"][CALENDAR_ID]["busy"]

    return len(busy) == 0