from fastapi import APIRouter, HTTPException, Header, Depends, Query
from pydantic import BaseModel
from typing import Optional
from app.services.auth_service import AuthService

from app.services.database_service import DatabaseService
from app.middlewares.auth_middlewares import verify_token

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
    result = AuthService.login_user(
        credentials.email, 
        credentials.password, 
        credentials.stay_logged_in  # ✅ Pass this flag to service
    )
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    # ✅ NEW: Ensure refresh_token is in response
    # (Your AuthService should generate it when stay_logged_in=True)
    return {
        "success": True,
        "access_token": result.get("access_token"),
        "refresh_token": result.get("refresh_token"),  # ✅ Add this
        "user": result.get("user"),
        "message": "Login successful"
    }


@router.get("/me")
async def get_current_user(authorization: str = Header(None)):
    """
    Get current authenticated user info from JWT token
    
    Header: Authorization: Bearer <token>
    Returns: { success: True, user: { email, full_name, company_name, trial_status } }
    """
    from app.middlewares.auth_middlewares import decode_token
    
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    # Extract Bearer token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'"
        )
    
    # Decode JWT
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    user_email = payload.get("email")
    
    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="Token missing email claim"
        )
    
    # Fetch user from database
    from app.services.database_service import db
    user_doc = db.users.find_one({"email": user_email})
    
    if not user_doc:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return {
        "success": True,
        "user": {
            "email": user_doc.get("email"),
            "full_name": user_doc.get("full_name", ""),
            "company_name": user_doc.get("company_name", ""),
            "trial_status": user_doc.get("trial_status", "ACTIVE"),
            "trial_end_date": user_doc.get("trial_end_date"),
        }
    }

@router.post("/logout")
async def logout(token: dict = Depends(verify_token)):
    """
    Logout user: invalidate refresh token in database
    
    Header: Authorization: Bearer <access_token>
    """
    user_email = token.get("email")
    
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Optional: Invalidate refresh tokens in DB
        DatabaseService.invalidate_refresh_tokens(user_email)
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        print(f"[ERROR] Logout failed for {user_email}: {e}")
        return {"success": True, "message": "Logged out"}  # Always succeed on logout

@router.post("/refresh-token")
async def refresh_token(refresh_token: str = Query(...)):
    """
    Refresh access token using refresh token
    
    Query: ?refresh_token=<token>
    Returns: { success: True, access_token: <new_token>, user: {...} }
    """
    from app.middlewares.auth_middlewares import decode_token
    
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token required"
        )
    
    # Decode refresh token
    payload = decode_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    
    # Fetch user and verify refresh token is valid
    try:
        user = DatabaseService.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate new access token
        new_access_token = AuthService.create_access_token(user_id, user["email"])
        
        return {
            "success": True,
            "access_token": new_access_token,
            "user": {
                "email": user["email"],
                "full_name": user.get("full_name", ""),
                "company_name": user.get("company_name", "")
            }
        }
    except Exception as e:
        print(f"[ERROR] Token refresh failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Token refresh failed"
        )


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

