import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """SMTP email service"""

    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL = os.getenv("SMTP_EMAIL")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        try:
            if not EmailService.SMTP_EMAIL or not EmailService.SMTP_PASSWORD:
                print("[EMAIL] SMTP_EMAIL or SMTP_PASSWORD missing")
                print("EMAIL:", EmailService.SMTP_EMAIL)
                print("PASSWORD:", EmailService.SMTP_PASSWORD)
                return False

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = EmailService.SMTP_EMAIL
            message["To"] = to_email

            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailService.SMTP_EMAIL, EmailService.SMTP_PASSWORD)
                server.sendmail(
                    EmailService.SMTP_EMAIL,
                    to_email,
                    message.as_string()
                )
            
            print(f"[EMAIL] Sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"[EMAIL] Send failed: {type(e).__name__}: {e}")
            return False