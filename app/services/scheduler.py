
from celery import Celery
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AbandonedCart, MessageSchedule, ConversationLog
from app.services.twilio_service import TwilioWhatsAppService
from app.services.ai_agent import WhatsAppAIAgent
from app.config import settings
import json
import logging
logger = logging.getLogger(__name__)
# Celery app configuration
celery_app = Celery("cart_recovery")
celery_app.conf.broker_url = settings.REDIS_URL
celery_app.conf.result_backend = settings.REDIS_URL
@celery_app.task(bind=True, max_retries=3)
def send_recovery_message(self, cart_id: str, message_type: str):
"""Send recovery message with retry logic"""
try:
db = next(get_db())
# Get cart data
cart = db.query(AbandonedCart).filter(AbandonedCart.cart_id == cart_id).first()
if not cart:
logger.error(f"Cart not found: {cart_id}")
return False
# Skip if cart is already recovered
if cart.cart_recovered:
logger.info(f"Cart already recovered: {cart_id}")
return True
# Prepare cart data for message generation
cart_data = {
"customer_name": cart.customer_name,
"product_name": cart.product_name,
"product_price": cart.product_price,
"quantity": cart.quantity,
"checkout_url": cart.checkout_url
}
# Generate message
ai_agent = WhatsAppAIAgent()
message = ai_agent.generate_template_message(message_type, cart_data)
# Send message
twilio_service = TwilioWhatsAppService()
success = twilio_service.send_message(cart.customer_whatsapp, message)
if success:
# Update cart metrics
cart.messages_sent += 1
# Log conversation
conversation_log = ConversationLog(
cart_id=cart_id,
customer_whatsapp=cart.customer_whatsapp,
message_type=\'sent\',
message_content=message
)
db.add(conversation_log)
# Update message schedule
schedule = db.query(MessageSchedule).filter(
MessageSchedule.cart_id == cart_id,
MessageSchedule.message_type == message_type
).first()
if schedule:
schedule.sent = True
schedule.sent_at = datetime.utcnow()
db.commit()
logger.info(f"Recovery message sent successfully: {cart_id} - {message_type}")
return True
else:
# Retry on failure
logger.warning(f"Failed to send message, retrying: {cart_id} - {message_type}")
raise Exception(f"Failed to send message for cart {cart_id}")
except Exception as e:
logger.error(f"Error in send_recovery_message: {e}")
# Retry with exponential backoff
raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
def schedule_recovery_sequence(cart_id: str):
"""Schedule the complete recovery message sequence"""
try:
db = next(get_db())
# Create message schedules
schedules = [
{
"message_type": "initial",
"delay_hours": 1
},
{
"message_type": "follow_up",
"delay_hours": 24
},
{
"message_type": "discount",
"delay_hours": 48
}
]
current_time = datetime.utcnow()
for schedule_data in schedules:
scheduled_time = current_time + timedelta(hours=schedule_data["delay_hours"])
# Create schedule record
schedule = MessageSchedule(
cart_id=cart_id,
message_type=schedule_data["message_type"],
scheduled_time=scheduled_time
)
db.add(schedule)
# Schedule Celery task
send_recovery_message.apply_async(
args=[cart_id, schedule_data["message_type"]],
eta=scheduled_time
)
db.commit()
logger.info(f"Recovery sequence scheduled for cart: {cart_id}")
except Exception as e:
logger.error(f"Error scheduling recovery sequence: {e}")
raise

