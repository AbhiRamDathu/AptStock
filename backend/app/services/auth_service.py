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
        """Verify password against hash (safe: never throw 500)"""
        try:
            if not hashed_password or not isinstance(hashed_password, str):
                return False
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            # This is the key: prevent 500 and log real reason in Render logs
            print(f"[AUTH] verify_password failed: {type(e).__name__}: {e}")
            return False

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
        """Authenticate user"""

        try:
            user = DatabaseService.get_user_by_email(email)

            if not user:
                return {"success": False, "error": "Invalid email or password"}

            password_hash = user.get("password_hash")

            if not password_hash:
                print(f"[ERROR] Missing password hash for user: {email}")
                return {"success": False, "error": "Account configuration error"}

        # Verify password safely
            if not AuthService.verify_password(password, password_hash):
                return {"success": False, "error": "Invalid email or password"}

        # Create tokens
            access_token = AuthService.create_access_token(user["id"], email)

            response = {
                "success": True,
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "full_name": user.get("full_name", ""),
                    "company_name": user.get("company_name", "")
                }
            }

            if stay_logged_in:
                refresh_token = AuthService.create_refresh_token(user["id"])
                response["refresh_token"] = refresh_token

            return response

        except Exception as e:
            print(f"[LOGIN ERROR] {e}")
            return {"success": False, "error": "Login failed"}

    @staticmethod
    def request_password_reset(email: str) -> Dict:
        """Request password reset: Generate OTP and send email"""
        try:
            print(f"[FORGOT_PASSWORD] request started for: {email}")

            user = DatabaseService.get_user_by_email(email)

            if not user:
                print(f"[FORGOT_PASSWORD] user not found for: {email}")
                return {
                    "success": True,
                    "message": "If email exists, reset code sent"
                }

        # Generate OTP
            otp_code = "{:06d}".format(random.randint(0, 999999))
            expiry = datetime.utcnow() + timedelta(minutes=10)

            print(f"[FORGOT_PASSWORD] OTP generated for: {email}")

        # Store OTP
            DatabaseService.set_reset_otp(email, otp_code, expiry)
            print(f"[FORGOT_PASSWORD] OTP stored for: {email}")

        # Send email
            email_sent = AuthService.send_password_reset_otp_email(email, otp_code)
            print(f"[FORGOT_PASSWORD] email_sent={email_sent} for: {email}")

            if not email_sent:
                return {
                    "success": False,
                    "error": "Failed to send reset email"
                }

            return {
                "success": True,
                "message": "Reset code sent successfully"
            }

        except Exception as e:
            print(f"[FORGOT_PASSWORD] request_password_reset failed: {type(e).__name__}: {e}")
            return {
                "success": False,
                "error": "Password reset request failed"
            }

    @staticmethod
    def send_password_reset_otp_email(email: str, otp_code: str) -> bool:
        """Send OTP email (6-digit code only, no link)"""
        try:
            if not SMTP_EMAIL or not SMTP_PASSWORD or not SMTP_SERVER or not SMTP_PORT:
                print("[FORGOT_PASSWORD] SMTP config missing")
                print(f"SMTP_SERVER: {SMTP_SERVER}")
                print(f"SMTP_PORT: {SMTP_PORT}")
                print(f"SMTP_EMAIL exists: {bool(SMTP_EMAIL)}")
                print(f"SMTP_PASSWORD exists: {bool(SMTP_PASSWORD)}")
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

            print(f"[FORGOT_PASSWORD] sending OTP email to {email}")
            print(f"[FORGOT_PASSWORD] SMTP server: {SMTP_SERVER}:{SMTP_PORT}")

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
                server.starttls()
                server.login(SMTP_EMAIL, SMTP_PASSWORD)
                server.send_message(msg)

            print(f"[FORGOT_PASSWORD] email sent successfully to {email}")
            return True

        except Exception as e:
            print(f"[FORGOT_PASSWORD] Email send failed: {type(e).__name__}: {e}")
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