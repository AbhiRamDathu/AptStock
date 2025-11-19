import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """Service for sending emails"""
    
    # Gmail SMTP Configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")
    
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        """
        Send HTML email using Gmail SMTP
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = EmailService.SENDER_EMAIL
            message["To"] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()  # Secure connection
                server.login(EmailService.SENDER_EMAIL, EmailService.SENDER_PASSWORD)
                server.sendmail(EmailService.SENDER_EMAIL, to_email, message.as_string())
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False
