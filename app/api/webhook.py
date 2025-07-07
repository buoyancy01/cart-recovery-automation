
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AbandonedCart
from app.services.scheduler import schedule_recovery_sequence
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
router = APIRouter()
class WebhookCartData(BaseModel):
cart_id: str
customer_name: str
customer_whatsapp: str
product_name: str
product_price: float
quantity: int
checkout_url: str
@router.post("/webhook/abandoned-cart")
async def handle_abandoned_cart(
cart_data: WebhookCartData,
background_tasks: BackgroundTasks,
db: Session = Depends(get_db)
):
"""Handle abandoned cart webhook from e-commerce platform"""
try:
# Check if cart already exists
existing_cart = db.query(AbandonedCart).filter(
AbandonedCart.cart_id == cart_data.cart_id
).first()
if existing_cart:
logger.info(f"Cart already exists: {cart_data.cart_id}")
return {"status": "success", "message": "Cart already processed"}
# Create new abandoned cart record
abandoned_cart = AbandonedCart(
cart_id=cart_data.cart_id,
customer_name=cart_data.customer_name,
customer_whatsapp=cart_data.customer_whatsapp,
product_name=cart_data.product_name,
product_price=cart_data.product_price,
quantity=cart_data.quantity,
checkout_url=cart_data.checkout_url
)
db.add(abandoned_cart)
db.commit()
# Schedule recovery sequence in background
background_tasks.add_task(schedule_recovery_sequence, cart_data.cart_id)
logger.info(f"Abandoned cart processed: {cart_data.cart_id}")
return {
"status": "success",
"message": "Cart recovery initiated",
"cart_id": cart_data.cart_id
}
except Exception as e:
logger.error(f"Error processing abandoned cart: {e}")
raise HTTPException(status_code=500, detail="Internal server error")
@router.post("/webhook/cart-recovered")
async def handle_cart_recovered(
cart_id: str,
revenue: float,
db: Session = Depends(get_db)
):
"""Handle cart recovery webhook when customer completes purchase"""
try:
cart = db.query(AbandonedCart).filter(AbandonedCart.cart_id == cart_id).first()
if not cart:
raise HTTPException(status_code=404, detail="Cart not found")
# Update cart as recovered
cart.cart_recovered = True
cart.recovery_revenue = revenue
cart.recovered_at = datetime.utcnow()
db.commit()
logger.info(f"Cart recovered: {cart_id} - Revenue: R$ {revenue}")
return {
"status": "success",
"message": "Cart recovery recorded",
"cart_id": cart_id,
"revenue": revenue
}
except Exception as e:
logger.error(f"Error recording cart recovery: {e}")
raise HTTPException(status_code=500, detail="Internal server error")

