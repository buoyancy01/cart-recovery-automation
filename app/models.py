
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base
class AbandonedCart(Base):
__tablename__ = "abandoned_carts"
id = Column(Integer, primary_key=True, index=True)
cart_id = Column(String(255), unique=True, index=True)
customer_whatsapp = Column(String(20), index=True)
customer_name = Column(String(255))
product_name = Column(String(255))
product_price = Column(Float)
quantity = Column(Integer)
checkout_url = Column(Text)
# Recovery metrics
messages_sent = Column(Integer, default=0)
customer_responded = Column(Boolean, default=False)
cart_recovered = Column(Boolean, default=False)
recovery_revenue = Column(Float, default=0.0)
# Timestamps
created_at = Column(DateTime(timezone=True), server_default=func.now())
updated_at = Column(DateTime(timezone=True), onupdate=func.now())
recovered_at = Column(DateTime(timezone=True), nullable=True)
class ConversationLog(Base):
__tablename__ = "conversation_logs"
id = Column(Integer, primary_key=True, index=True)
cart_id = Column(String(255), index=True)
customer_whatsapp = Column(String(20))
message_type = Column(String(50)) # 'sent' or 'received'
message_content = Column(Text)
timestamp = Column(DateTime(timezone=True), server_default=func.now())
class MessageSchedule(Base):
__tablename__ = "message_schedules"
id = Column(Integer, primary_key=True, index=True)
cart_id = Column(String(255), index=True)
message_type = Column(String(50)) # 'initial', 'follow_up', 'discount'
scheduled_time = Column(DateTime(timezone=True))
sent = Column(Boolean, default=False)
sent_at = Column(DateTime(timezone=True), nullable=True)


