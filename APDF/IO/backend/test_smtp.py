import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("lingarajuvelishala11@gmail.com")
SMTP_PASSWORD = os.getenv("hwmkojbxccfvclor")

print(f"Testing SMTP with:")
print(f"Server: {SMTP_SERVER}:{SMTP_PORT}")
print(f"Email: {SMTP_EMAIL}")
print(f"Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")

try:
    msg = MIMEText("This is a test email from ForecastAI Pro")
    msg["Subject"] = "Test Email"
    msg["From"] = SMTP_EMAIL
    msg["To"] = SMTP_EMAIL
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
    
    print("\n✅ Email sent successfully! Check your inbox.")
except Exception as e:
    print(f"\n❌ Failed to send email: {e}")
