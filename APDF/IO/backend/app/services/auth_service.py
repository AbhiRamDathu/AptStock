import secrets
import random
import smtplib
from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext
from jose import JWTError, jwt
from email.mime.text import MIMEText


from app.config import (
    JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS,
    REFRESH_TOKEN_EXPIRATION_DAYS, SMTP_SERVER, SMTP_PORT,
    SMTP_EMAIL, SMTP_PASSWORD
)
from app.services.database_service import DatabaseService


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class AuthService:
   
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)


    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)


    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        """Create JWT access token"""
        payload = {
            "sub": user_id,
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token


    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create refresh token"""
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS),
            "iat": datetime.utcnow()
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        DatabaseService.store_refresh_token(user_id, token)
        return token


    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError:
            return None


    @staticmethod
    def register_user(email: str, password: str, full_name: str, company_name: str) -> Dict:
        """Register new user"""
        existing_user = DatabaseService.get_user_by_email(email)
        if existing_user:
            return {"success": False, "error": "Email already registered"}


        password_hash = AuthService.hash_password(password)
        user_id = DatabaseService.create_user({
            "email": email,
            "password_hash": password_hash,
            "full_name": full_name,
            "company_name": company_name
        })


        if not user_id:
            return {"success": False, "error": "Registration failed"}


        return {"success": True, "user_id": user_id, "email": email}


    @staticmethod
    def login_user(email: str, password: str, stay_logged_in: bool = False) -> Dict:
        """
        Authenticate user and generate tokens
    
        Args:
            email: User email
            password: User password
            stay_logged_in: If True, generate 7-day refresh token
        
        Returns:
            {
                "success": True,
                "access_token": JWT token (15 min),
                "refresh_token": Refresh token (7 days, if stay_logged_in=True),
                "token_type": "bearer",
                "user": User data
            }
        """
        user = DatabaseService.get_user_by_email(email)
   
        if not user or not AuthService.verify_password(password, user.get("password_hash", "")):
            return {"success": False, "error": "Invalid email or password"}

    # ✅ Generate access token (15 minutes)
        access_token = AuthService.create_access_token(user["id"], email)
    
    # ✅ Initialize response
        response = {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": None,  # ✅ NEW: Always include this key
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user.get("full_name", ""),
                "company_name": user.get("company_name", "")
            }
        }

    # ✅ Generate refresh token (7 days) ONLY if stay_logged_in=True
        if stay_logged_in:
            refresh_token = AuthService.create_refresh_token(user["id"])
            response["refresh_token"] = refresh_token
            print(f"✅ 7-day refresh token generated for {email}")
        else:
            print(f"ℹ️  No refresh token (stay_logged_in=False)")

        return response


    @staticmethod
    def request_password_reset(email: str) -> Dict:
        """Request password reset: Generate OTP and SEND EMAIL"""
        try:
            user = DatabaseService.get_user_by_email(email)
            if not user:
                return {"success": True, "message": "If email exists, reset code sent"}


            # Generate 6-digit OTP
            otp_code = "{:06d}".format(random.randint(0, 999999))
            expiry = datetime.utcnow() + timedelta(minutes=10)


            # Store OTP in database
            DatabaseService.set_reset_otp(email, otp_code, expiry)
            print(f"[DEBUG] OTP stored for {email}: {otp_code}")


            # SEND EMAIL WITH OTP - THIS IS THE KEY!
            email_sent = AuthService.send_password_reset_otp_email(email, otp_code)
           
            if email_sent:
                print(f"[SUCCESS] OTP email sent for {email}")
                return {"success": True, "message": "Reset code sent"}
            else:
                print(f"[ERROR] Failed to send email for {email}")
                return {"success": True, "message": "If email exists, reset code sent"}


        except Exception as e:
            print(f"[ERROR] in request_password_reset: {e}")
            return {"success": True, "message": "If email exists, reset code sent"}


    @staticmethod
    def send_password_reset_otp_email(email: str, otp_code: str) -> bool:
        """Send OTP email (6-digit code only, no link)"""
        try:
            # Validate SMTP credentials
            if not SMTP_EMAIL or not SMTP_PASSWORD:
                print(f"[ERROR] SMTP credentials not configured!")
                print(f"SMTP_EMAIL: {SMTP_EMAIL}")
                pwd_masked = '*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'
                print(f"SMTP_PASSWORD: {pwd_masked}")
                return False


            subject = "Your ForecastAI Pro Password Reset Code"
            body = f"""Hello,


Use this 6-digit code to reset your ForecastAI Pro password:


{otp_code}


This code expires in 10 minutes.
DO NOT share this code with anyone.


If you didn't request this, please ignore this email.


---
ForecastAI Pro Team
"""
           
            msg = MIMEText(body, "plain")
            msg["From"] = SMTP_EMAIL
            msg["To"] = email
            msg["Subject"] = subject


            print(f"[INFO] Sending OTP email to {email}")
            print(f"[INFO] SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")


            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)


            print(f"[SUCCESS] OTP {otp_code} sent to {email}")
            return True


        except Exception as e:
            print(f"[ERROR] Email send failed: {e}")
            print(f"[ERROR] Exception type: {type(e).__name__}")
            return False


    @staticmethod
    def verify_and_reset_password(email: str, otp_code: str, new_password: str) -> Dict:
        """Verify OTP and reset password"""
        try:
            user = DatabaseService.get_user_by_email(email)
            if not user:
                return {"success": False, "error": "Email not found"}


            # Check OTP validity
            if (
                user.get("reset_otp") != otp_code or
                user.get("reset_otp_used", False) or
                datetime.utcnow() > user.get("reset_otp_expiry", datetime.utcnow())
            ):
                return {"success": False, "error": "Invalid or expired OTP"}


            # Hash and update password
            password_hash = AuthService.hash_password(new_password)
            DatabaseService.update_user_password(email, password_hash)
            DatabaseService.mark_reset_otp_used(email)


            return {"success": True, "message": "Password reset successfully"}
        except Exception as e:
            print(f"[ERROR] in verify_and_reset_password: {e}")
            return {"success": False, "error": "Password reset failed"}