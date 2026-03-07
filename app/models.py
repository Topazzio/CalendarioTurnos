from pydantic import BaseModel
from datetime import datetime

class BookingRequest(BaseModel):
    name: str
    phone: str
    start_time: datetime