import os
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
# Twilio Configuration
TWILIO_ACCOUNT_SID: str
TWILIO_AUTH_TOKEN: str
TWILIO_WHATSAPP_NUMBER: str
# OpenAI Configuration
OPENAI_API_KEY: str
# Redis Configuration
REDIS_URL: str = "redis://localhost:6379"
# Database Configuration
DATABASE_URL: str
# Webhook Configuration
WEBHOOK_SECRET: str = "your-webhook-secret"
# Application Settings
DEBUG: bool = False
class Config:
env_file = ".env"
settings = Settings()

