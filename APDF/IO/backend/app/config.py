"""
Configuration file for ForecastAI Pro Backend
Loads all environment variables and exports them
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ========== MONGODB CONFIGURATION ==========
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "forecastai_pro")

# MongoDB Collections
USERS_COLLECTION = "users"
PASSWORD_RESET_TOKENS_COLLECTION = "password_reset_tokens"

# ========== JWT AUTHENTICATION ==========
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key-CHANGE-THIS-IN-PRODUCTION-min-32-chars")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", "7"))

# ========== EMAIL CONFIGURATION (for password reset) ==========
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ========== FRONTEND URL (for email links) ==========
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# ========== LOGGING ==========
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ========== VALIDATION ==========
print("\n" + "="*60)
print("🔧 Configuration Loaded")
print("="*60)
print(f"📊 Database: {DATABASE_NAME}")
print(f"🔐 JWT Secret: {'*' * 20} (hidden)")
print(f"📧 SMTP Email: {SMTP_EMAIL or 'Not configured'}")
print(f"🌐 Frontend URL: {FRONTEND_URL}")
print("="*60 + "\n")

# Warn if using defaults
if JWT_SECRET == "your-super-secret-key-CHANGE-THIS-IN-PRODUCTION-min-32-chars":
    print("⚠️  WARNING: Using default JWT_SECRET! Change this in production!")

if not SMTP_EMAIL or not SMTP_PASSWORD:
    print("⚠️  WARNING: SMTP not configured. Password reset emails will fail!")
