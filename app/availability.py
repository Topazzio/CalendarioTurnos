from datetime import datetime, timedelta, date
import pytz
from schedule import generate_day_slots
from google_calendar import get_busy_times

TZ = pytz.timezone("America/Argentina/Cordoba")

DAY_NAMES = [
    "Lunes","Martes","Miércoles",
    "Jueves","Viernes","Sábado","Domingo"
]


def overlap(a_start, a_end, b_start, b_end):
    return a_start < b_end and a_end > b_start


def build_week_availability(start_date: date):

    week_data = []
    now = datetime.now(TZ)

    for i in range(7):
        current_day = start_date + timedelta(days=i)
        slots = generate_day_slots(current_day)

        busy_times = get_busy_times(current_day)

        parsed_busy = []
        for b in busy_times:
            parsed_busy.append((
                datetime.fromisoformat(b["start"].replace("Z","+00:00")),
                datetime.fromisoformat(b["end"].replace("Z","+00:00"))
            ))

        day_slots = []

        for slot in slots:

            available = True

            # ❌ bloquear pasado
            if slot["start"] <= now:
                available = False

            for bs, be in parsed_busy:
                if overlap(slot["start"], slot["end"], bs, be):
                    available = False
                    break

            day_slots.append({
                "time": slot["start"].strftime("%H:%M"),
                "start": slot["start"].isoformat(),
                "available": available
            })

        week_data.append({
            "date": current_day.isoformat(),
            "day_name": DAY_NAMES[current_day.weekday()],
            "slots": day_slots
        })

    return week_data