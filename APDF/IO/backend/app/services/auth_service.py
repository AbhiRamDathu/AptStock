from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
from app.services.database_service import DatabaseService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        """✅ FIXED: Create JWT with proper Unix timestamp"""
        exp_time = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        payload = {
            "sub": user_id,
            "email": email,
            "exp": int(exp_time.timestamp()),  # ✅ Must be int
            "iat": int(datetime.utcnow().timestamp()),
            "type": "access"
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def login_user(email: str, password: str, stay_logged_in: bool = False) -> dict:
        user = DatabaseService.get_user_by_email(email)
        
        if not user or not user.get("password_hash"):
            return {"success": False, "error": "Invalid email or password"}
        
        if not AuthService.verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Invalid email or password"}
        
        access_token = AuthService.create_access_token(user["id"], email)
        
        return {
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
