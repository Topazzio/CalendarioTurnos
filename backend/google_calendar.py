from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os
import json
from zoneinfo import ZoneInfo


SCOPES = ['https://www.googleapis.com/auth/calendar']

CALENDAR_ID = "e8792ead27291cf084c84035f6def39542154d65524de10263172dbb7e996b18@group.calendar.google.com"
TIMEZONE = "America/Argentina/Cordoba"

def get_calendar_service():

    credentials_json = os.environ.get("GOOGLE_CREDENTIALS")

    credentials_info = json.loads(credentials_json)

    creds = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=creds)

    return service


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