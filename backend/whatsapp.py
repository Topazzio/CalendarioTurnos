from twilio.rest import Client
import os

def send_whatsapp(to_number, message):
    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))

    client.messages.create(
        from_='whatsapp:+14155238886',
        body=message,
        to=f'whatsapp:{to_number}'
    )