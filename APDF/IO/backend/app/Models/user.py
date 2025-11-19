from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # OTP Fields - ADD THESE
    otp_code: Optional[str] = None
    otp_expires_at: Optional[datetime] = None
    otp_attempts: int = 0

class UserInDB(User):
    hashed_password: str
