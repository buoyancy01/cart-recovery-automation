
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from app.config import settings
import logging
logger = logging.getLogger(__name__)
class TwilioWhatsAppService:
def __init__(self):
self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
def send_message(self, to_number: str, message: str) -> bool:
"""Send WhatsApp message via Twilio"""
try:
# Ensure phone number format
if not to_number.startswith("+"):
to_number = "+" + to_number
message_obj = self.client.messages.create(
body=message,
from_=f"whatsapp:{self.whatsapp_number}",
to=f"whatsapp:{to_number}"
)
logger.info(f"Message sent successfully: {message_obj.sid}")
return True
except Exception as e:
logger.error(f"Error sending message to {to_number}: {e}")
return False
def create_response(self, message: str) -> str:
"""Create TwiML response for incoming messages"""
response = MessagingResponse()
response.message(message)
return str(response)
def validate_webhook(self, request_data: dict) -> bool:
"""Validate incoming webhook from Twilio"""
# Add webhook validation logic here
return True

