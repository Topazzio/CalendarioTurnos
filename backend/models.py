from pydantic import BaseModel
from datetime import datetime

class BookingRequest(BaseModel):
    name: str
    phone: str
    auto: str
    pago: str
    anio: str
    material: str
    start_time: datetime