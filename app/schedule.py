from datetime import datetime, timedelta, time
import pytz

TZ = pytz.timezone("America/Argentina/Cordoba")

def get_working_hours(date):
    weekday = date.weekday()

    # Domingo cerrado
    if weekday == 6:
        return None

    # Lunes a viernes
    if weekday <= 4:
        return time(12, 0), time(18, 0)

    # Sábado
    return time(12, 0), time(16, 0)


def generate_day_slots(date):
    hours = get_working_hours(date)
    if not hours:
        return []

    start_time, end_time = hours

    current = TZ.localize(datetime.combine(date, start_time))
    end_limit = TZ.localize(datetime.combine(date, end_time))

    slots = []

    while current < end_limit:
        slot_end = current + timedelta(hours=1)

        slots.append({
            "start": current,
            "end": slot_end
        })

        current += timedelta(hours=1)

    return slots