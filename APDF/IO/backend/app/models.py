from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List

# ========== AUTHENTICATION MODELS ==========

class UserRegistration(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1, description="User's full name")
    company_name: str = Field(..., min_length=1, description="Company name")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123",
                "full_name": "Priya Kumar",
                "company_name": "Kumar Retail Store"
            }
        }


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str
    stay_logged_in: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123",
                "stay_logged_in": True
            }
        }


class UserInDB(BaseModel):
    """User database model (internal use)"""
    id: str
    email: str
    full_name: str
    company_name: str
    password_hash: str
    created_at: datetime
    is_verified: bool = False
    refresh_tokens: List[str] = []


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: dict


class PasswordResetRequest(BaseModel):
    """Password reset request model"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""
    token: str
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters")


class UserResponse(BaseModel):
    """User information response"""
    id: str
    email: str
    full_name: str
    company_name: str
    created_at: datetime

class SalesRecord(BaseModel):
    date: date
    sku: str
    store: str
    units_sold: int


class ForecastPoint(BaseModel):
    date: date
    predicted_units: float
    lower_ci: Optional[float]
    upper_ci: Optional[float]


class ForecastRequest(BaseModel):
    skus: List[str]
    store: str


class ForecastResponseItem(BaseModel):
    sku: str
    forecast: List[ForecastPoint]


class ForecastResponse(BaseModel):
    forecast: List[ForecastResponseItem]


class HistoricalRequest(BaseModel):
    skus: List[str]
    store: str
    from_date: date
    to_date: date


class HistoricalResponseItem(BaseModel):
    date: date
    sku: str
    store: str
    units_sold: int


class SKUsResponse(BaseModel):
    skus: List[str]


