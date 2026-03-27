import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """SMTP email service"""

    SMTP_SERVER = (os.getenv("SMTP_SERVER") or "smtp.gmail.com").strip()
    SMTP_PORT = int((os.getenv("SMTP_PORT") or "587").strip())
    SMTP_EMAIL = (os.getenv("SMTP_EMAIL") or "").strip()
    SMTP_PASSWORD = (os.getenv("SMTP_PASSWORD") or "").strip()

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        try:
            to_email = (to_email or "").strip().lower()

            print(f"[EMAIL DEBUG]")
            print(f"SMTP_EMAIL: {EmailService.SMTP_EMAIL}")
            print(f"TO_EMAIL: {to_email}")
            print(f"SMTP_SERVER: {EmailService.SMTP_SERVER}")
            print(f"SMTP_PORT: {EmailService.SMTP_PORT}")

            if not EmailService.SMTP_EMAIL or not EmailService.SMTP_PASSWORD:
                print("[EMAIL] SMTP_EMAIL or SMTP_PASSWORD missing")
                print(f"[EMAIL] SMTP_EMAIL={EmailService.SMTP_EMAIL}")
                print(f"[EMAIL] SMTP_PASSWORD_PRESENT={bool(EmailService.SMTP_PASSWORD)}")
                return False

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = EmailService.SMTP_EMAIL
            message["To"] = to_email
            message.attach(MIMEText(html_content, "html"))

            print(f"[EMAIL] SMTP_SERVER={EmailService.SMTP_SERVER}")
            print(f"[EMAIL] SMTP_PORT={EmailService.SMTP_PORT}")
            print(f"[EMAIL] SMTP_EMAIL={EmailService.SMTP_EMAIL}")
            print(f"[EMAIL] TO_EMAIL={to_email}")

            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(EmailService.SMTP_EMAIL, EmailService.SMTP_PASSWORD)
                server.sendmail(
                    EmailService.SMTP_EMAIL,
                    [to_email],
                    message.as_string()
                )

            print(f"[EMAIL] Sent successfully to {to_email}")
            return True

        except smtplib.SMTPRecipientsRefused as e:
            print(f"[EMAIL] SMTPRecipientsRefused for {to_email}: {e.recipients}")
            return False
        except smtplib.SMTPAuthenticationError as e:
            print(f"[EMAIL] SMTPAuthenticationError: {e}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            print(f"[EMAIL] SMTPServerDisconnected: {e}")
            return False
        except smtplib.SMTPException as e:
            print(f"[EMAIL] SMTPException for {to_email}: {type(e).__name__}: {e}")
            return False
        except Exception as e:
            print(f"[EMAIL] Send failed for {to_email}: {type(e).__name__}: {e}")
            return False