import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

print(f"Testing SMTP:")
print(f"Server: {SMTP_SERVER}:{SMTP_PORT}")
print(f"Email: {SMTP_EMAIL}")
print(f"Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")

try:
    msg = MIMEText("Test email from ForecastAI Pro - OTP system working!")
    msg["Subject"] = "Test - OTP Email System"
    msg["From"] = SMTP_EMAIL
    msg["To"] = SMTP_EMAIL
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
    
    print("\n✅ SUCCESS! Email sent. Check your inbox.")
except Exception as e:
    print(f"\n❌ FAILED: {e}")
