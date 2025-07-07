
from fastapi import APIRouter, HTTPException, Form, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AbandonedCart, ConversationLog
from app.services.twilio_service import TwilioWhatsAppService
from app.services.ai_agent import WhatsAppAIAgent
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
router = APIRouter()
@router.post("/whatsapp/webhook")
async def handle_whatsapp_message(
From: str = Form(...),
Body: str = Form(...),
db: Session = Depends(get_db)
):
"""Handle incoming WhatsApp messages from Twilio"""
try:
# Extract phone number (remove 'whatsapp:' prefix)
customer_whatsapp = From.replace('whatsapp:', '').replace('+', '')
message_body = Body.strip()
logger.info(f"Received message from {customer_whatsapp}: {message_body}")
# Find active abandoned cart for this customer
cart = db.query(AbandonedCart).filter(
AbandonedCart.customer_whatsapp == customer_whatsapp,
AbandonedCart.cart_recovered == False
).order_by(AbandonedCart.created_at.desc()).first()
if not cart:
# Send generic response for unknown customers
response_message = "Olá! Obrigado por entrar em contato. Se você tem alguma dúvida\nsobre nossos produtos, será um prazer ajudá-lo!"
else:
# Mark customer as responded
cart.customer_responded = True
# Log incoming message
conversation_log = ConversationLog(
cart_id=cart.cart_id,
customer_whatsapp=customer_whatsapp,
message_type='received',
message_content=message_body
)
db.add(conversation_log)
# Generate AI response
cart_context = {
'customer_name': cart.customer_name,
'product_name': cart.product_name,
'product_price': cart.product_price,
'quantity': cart.quantity,
'checkout_url': cart.checkout_url
}
ai_agent = WhatsAppAIAgent()
response_message = ai_agent.generate_contextual_response(message_body, cart_context)
# Log outgoing response
response_log = ConversationLog(
cart_id=cart.cart_id,
customer_whatsapp=customer_whatsapp,
message_type='sent',
message_content=response_message
)
db.add(response_log)
# Update message counter
cart.messages_sent += 1
db.commit()
# Create TwiML response
twilio_service = TwilioWhatsAppService()
twiml_response = twilio_service.create_response(response_message)
return twiml_response
except Exception as e:
logger.error(f"Error handling WhatsApp message: {e}")
# Return generic error response
twilio_service = TwilioWhatsAppService()
error_response = "Desculpe, estou com dificuldades técnicas no momento. Tente novamente\nem alguns minutos."
return twilio_service.create_response(error_response)


