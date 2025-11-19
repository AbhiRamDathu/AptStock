from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from app.services.auth_service import AuthService

router = APIRouter()

# ============ MODELS ============
class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str
    company_name: str

class UserLogin(BaseModel):
    email: str
    password: str
    stay_logged_in: bool = False

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    email: str
    otp: str
    new_password: str

# ============ ROUTES ============

@router.post("/register", status_code=201)
async def register(user: UserRegistration):
    """Register new user"""
    result = AuthService.register_user(user.email, user.password, user.full_name, user.company_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/login")
async def login(credentials: UserLogin):
    """Login user"""
    result = AuthService.login_user(credentials.email, credentials.password, credentials.stay_logged_in)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    return result

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """Request password reset OTP"""
    result = AuthService.request_password_reset(request.email)
    return result

@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """Reset password with OTP"""
    result = AuthService.verify_and_reset_password(request.email, request.otp, request.new_password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}

