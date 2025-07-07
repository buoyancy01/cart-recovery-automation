
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import AbandonedCart, ConversationLog
from datetime import datetime, timedelta
from typing import Optional
router = APIRouter()
@router.get("/analytics/dashboard")
async def get_dashboard_analytics(
days: int = Query(default=30, description="Number of days to analyze"),
db: Session = Depends(get_db)
):
"""Get dashboard analytics for cart recovery performance"""
# Calculate date range
end_date = datetime.utcnow()
start_date = end_date - timedelta(days=days)
# Total abandoned carts
total_carts = db.query(AbandonedCart).filter(
AbandonedCart.created_at >= start_date
).count()
# Recovered carts
recovered_carts = db.query(AbandonedCart).filter(
AbandonedCart.created_at >= start_date,
AbandonedCart.cart_recovered == True
).count()
# Recovery rate
recovery_rate = (recovered_carts / total_carts * 100) if total_carts > 0 else 0
# Total recovery revenue
total_revenue = db.query(func.sum(AbandonedCart.recovery_revenue)).filter(
AbandonedCart.created_at >= start_date,
AbandonedCart.cart_recovered == True
).scalar() or 0
# Average recovery time
avg_recovery_time = db.query(
func.avg(
func.extract("epoch", AbandonedCart.recovered_at - AbandonedCart.created_at)
)
).filter(
AbandonedCart.created_at >= start_date,
AbandonedCart.cart_recovered == True
).scalar()
avg_recovery_hours = int(avg_recovery_time / 3600) if avg_recovery_time else 0
# Messages sent
total_messages = db.query(func.sum(AbandonedCart.messages_sent)).filter(
AbandonedCart.created_at >= start_date
).scalar() or 0
# Customer response rate
responded_customers = db.query(AbandonedCart).filter(
AbandonedCart.created_at >= start_date,
AbandonedCart.customer_responded == True
).count()
response_rate = (responded_customers / total_carts * 100) if total_carts > 0 else 0
return {
"period": {
"start_date": start_date.isoformat(),
"end_date": end_date.isoformat(),
"days": days
},
"metrics": {
"total_abandoned_carts": total_carts,
"recovered_carts": recovered_carts,
"recovery_rate": round(recovery_rate, 2),
"total_revenue": round(total_revenue, 2),
"average_recovery_time_hours": avg_recovery_hours,
"total_messages_sent": total_messages,
"customer_response_rate": round(response_rate, 2),
"average_messages_per_cart": round(total_messages / total_carts, 2) if total_carts >
0 else 0
}
}
@router.get("/analytics/carts")
async def get_cart_analytics(
limit: int = Query(default=50, description="Number of carts to return"),
offset: int = Query(default=0, description="Offset for pagination"),
status: Optional[str] = Query(default=None, description="Filter by status: recovered,\npending, responded"),
db: Session = Depends(get_db)
):
"""Get detailed cart analytics with pagination"""
query = db.query(AbandonedCart)
# Apply filters
if status == "recovered":
query = query.filter(AbandonedCart.cart_recovered == True)
elif status == "pending":
query = query.filter(AbandonedCart.cart_recovered == False)
elif status == "responded":
query = query.filter(AbandonedCart.customer_responded == True)
# Get total count
total_count = query.count()
# Apply pagination and ordering
carts = query.order_by(AbandonedCart.created_at.desc()).offset(offset).limit(limit).all()
# Format response
cart_data = []
for cart in carts:
cart_data.append({
"cart_id": cart.cart_id,
"customer_name": cart.customer_name,
"customer_whatsapp": cart.customer_whatsapp,
"product_name": cart.product_name,
"product_price": cart.product_price,
"quantity": cart.quantity,
"messages_sent": cart.messages_sent,
"customer_responded": cart.customer_responded,
"cart_recovered": cart.cart_recovered,
"recovery_revenue": cart.recovery_revenue,
"created_at": cart.created_at.isoformat(),
"recovered_at": cart.recovered_at.isoformat() if cart.recovered_at else None,
"recovery_time_hours": int((cart.recovered_at - cart.created_at).total_seconds() /\
3600) if cart.recovered_at else None
})
return {
"total_count": total_count,
"carts": cart_data,
"pagination": {
"limit": limit,
"offset": offset,
"has_more": offset + limit < total_count
}
}

