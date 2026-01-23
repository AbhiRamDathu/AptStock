# ✅ COMPLETE: app/middleware/auth.py
# JWT Authentication Middleware for FastAPI

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime
import logging
from typing import Optional, Dict
from app.services.database_service import DatabaseService, db

from app.config import JWT_SECRET, JWT_ALGORITHM

# ✅ Setup logging
logger = logging.getLogger(__name__)

# ✅ Security scheme for API endpoints
security = HTTPBearer()

class TrialManager:
    """
    ✅ Manages trial status checking for free trial users
    
    Trial Flow:
    - Day 1-14: trial_status = "ACTIVE" → Allow access
    - Day 15+: trial_status = "EXPIRED" → Block access, return 402
    - PAID: trial_status = "PAID" → Check subscription, allow if valid
    """
    
    TRIAL_DURATION_DAYS = 14
    ADMIN_EMAILS = ["your-email@gmail.com"]  # ← UPDATE WITH YOUR EMAIL
    
    @staticmethod
    def check_trial_status(email: str) -> tuple[str, Optional[str]]:
        """
        Check if user's trial is still active
        
        Returns:
            tuple: (status, error_message)
            - ("ALLOWED", None) → User can proceed
            - ("BLOCKED", error_msg) → Return 402 to user
        """
        
        # ✅ FOUNDER BYPASS: Admins always have access
        if email in TrialManager.ADMIN_EMAILS:
            logger.info(f"👑 FOUNDER BYPASS: {email}")
            return ("ALLOWED", None)
        
        try:
            # Get user from database
            user = db.users.find_one({"email": email})
            
            if not user:
                logger.error(f"User not found: {email}")
                return ("BLOCKED", "User account not found")
            
            # Get trial information
            trial_status = user.get("trial_status", "ACTIVE")
            trial_end_date = user.get("trial_end_date")
            subscription_end_date = user.get("subscription_end_date")

            # ✅ NEW: log what we read from MongoDB
            logger.info(
                f"[TRIAL] User={email}, status={trial_status}, "
                f"trial_end_date={trial_end_date}, subscription_end_date={subscription_end_date}"
            )
            
            # ✅ Case 1: PAID SUBSCRIPTION
            if trial_status == "PAID":
                if subscription_end_date:
                    # Check if subscription is still valid
                    from datetime import datetime
                    if datetime.utcnow() < subscription_end_date:
                        logger.info(f"✅ PAID SUBSCRIBER: {email}")
                        return ("ALLOWED", None)
                    else:
                        logger.info(f"💳 SUBSCRIPTION EXPIRED: {email}")
                        # Update status
                        db.users.update_one(
                            {"email": email},
                            {"$set": {"trial_status": "EXPIRED"}}
                        )
                        return ("BLOCKED", "Subscription expired. Please renew to continue.")
                else:
                    logger.info(f"✅ PAID SUBSCRIBER: {email}")
                    return ("ALLOWED", None)
            
            # ✅ Case 2: ACTIVE TRIAL
            if trial_status == "ACTIVE":
                if trial_end_date:
                    from datetime import datetime
                    if datetime.utcnow() < trial_end_date:
                        logger.info(f"✅ TRIAL ACTIVE ({(trial_end_date - datetime.utcnow()).days} days): {email}")
                        return ("ALLOWED", None)
                    else:
                        # Trial expired - update status
                        logger.info(f"⏰ TRIAL EXPIRED: {email}")
                        db.users.update_one(
                            {"email": email},
                            {"$set": {"trial_status": "EXPIRED"}}
                        )
                        return ("BLOCKED", "Your 14-day free trial has ended. Please upgrade to continue.")
                else:
                    logger.warning(f"⚠️  User has ACTIVE status but no trial_end_date: {email}")
                    return ("ALLOWED", None)
            
            # ✅ Case 3: ALREADY EXPIRED
            if trial_status == "EXPIRED":
                logger.info(f"🔒 TRIAL EXPIRED: {email}")
                logger.warning(f"[TRIAL] BLOCKING user={email}: trial_status=EXPIRED")
                return ("BLOCKED", "Your trial has expired. Please upgrade to Pro plan.")
            
            # Default: Block if unclear
            logger.warning(f"⚠️  Unknown trial_status: {trial_status}")
            return ("BLOCKED", "Trial status unknown")
            
        except Exception as e:
            logger.error(f"❌ Trial check error: {str(e)}")
            # In case of error, allow access (fail open)
            return ("ALLOWED", None)

# ═══════════════════════════════════════════════════════════════════════════════
# 1️⃣ MAIN: Verify JWT Token from Authorization Header
# ═══════════════════════════════════════════════════════════════════════════════

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    ✅ Verify JWT token from Bearer header
    
    Usage in routes:
    @router.post("/upload-and-process")
    async def upload_file(
        file: UploadFile = File(...),
        token: dict = Depends(verify_token)  # ← Add this parameter
    ):
        user_email = token.get('email', 'unknown')
        ...
    
    Expected header:
        Authorization: Bearer <jwt_token>
    
    Returns:
        dict: Token payload containing user info (sub, email, etc.)
    
    Raises:
        HTTPException: 401 if token invalid/expired
    """
    try:
        token = credentials.credentials
        logger.info(f"🔐 Verifying token: {token[:20]}...")
        
        # Decode JWT
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        
        # Extract user info
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        token_type: str = payload.get("type")
        
        if not user_id or not email:
            logger.warning("⚠️  Token missing required fields (sub, email)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing required fields",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if token_type != "access":
            logger.warning(f"⚠️  Wrong token type: {token_type} (expected: access)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. Use access token, not refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"✅ Token verified for user: {email}")
        
        # Return token payload (contains user info)
        return {
            "user_id": user_id,
            "email": email,
            "token_type": token_type,
            "sub": user_id,  # Keep original field name for compatibility
            **payload  # Include all other fields
        }
        
    except JWTError as e:
        logger.error(f"❌ JWT decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"❌ Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ═══════════════════════════════════════════════════════════════════════════════
# 2️⃣ OPTIONAL: Verify Token without raising exceptions (returns None if invalid)
# ═══════════════════════════════════════════════════════════════════════════════

def verify_token_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict]:
    """
    ✅ Verify JWT token but return None instead of raising exception
    
    Use when token is optional (some endpoints allow anonymous access)
    
    Returns:
        dict: Token payload if valid, None if invalid/missing
    """
    if not credentials:
        logger.info("⚠️  No credentials provided")
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        
        logger.info(f"✅ Optional token verified: {payload.get('email')}")
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            **payload
        }
        
    except JWTError as e:
        logger.warning(f"⚠️  Invalid optional token: {str(e)}")
        return None
    except Exception as e:
        logger.warning(f"⚠️  Optional token verification failed: {str(e)}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 3️⃣ DECODE: Extract token payload without FastAPI dependency
# ═══════════════════════════════════════════════════════════════════════════════

def decode_token(token: str) -> Optional[Dict]:
    """
    ✅ Decode JWT token directly (without FastAPI dependency)
    
    Use in service/utility functions:
        payload = decode_token(token_string)
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        logger.info(f"✅ Token decoded successfully: {payload.get('email')}")
        return payload
        
    except JWTError as e:
        logger.warning(f"⚠️  Failed to decode token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error decoding token: {str(e)}")
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# 4️⃣ VALIDATE: Check if token is still valid (not expired)
# ═══════════════════════════════════════════════════════════════════════════════

def is_token_valid(token: str) -> bool:
    """
    ✅ Check if JWT token is valid and not expired
    
    Use for quick validation:
        if is_token_valid(token_string):
            # Token is valid
    
    Args:
        token: JWT token string
    
    Returns:
        bool: True if valid, False if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        
        # Check expiration
        exp = payload.get("exp")
        if exp:
            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                logger.warning("⚠️  Token expired")
                return False
        
        logger.info("✅ Token is valid")
        return True
        
    except JWTError:
        logger.warning("⚠️  Invalid token")
        return False
    except Exception as e:
        logger.error(f"❌ Error validating token: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# 5️⃣ GET_USER: Extract user info from request token
# ═══════════════════════════════════════════════════════════════════════════════

def get_current_user(token: Dict = Depends(verify_token)) -> Dict:
    """
    ✅ Get current authenticated user from token
    
    Use in protected routes to get user info:
        @router.get("/profile")
        async def get_profile(user: Dict = Depends(get_current_user)):
            return {"user": user['email']}
    
    Args:
        token: Verified token (via verify_token dependency)
    
    Returns:
        dict: User information (user_id, email, etc.)
    """
    return {
        "user_id": token.get("user_id"),
        "email": token.get("email"),
        "sub": token.get("sub")
    }

# ═══════════════════════════════════════════════════════════════════════════════
# 6️⃣ EXTRACT_BEARER: Extract JWT string from Authorization header
# ═══════════════════════════════════════════════════════════════════════════════

def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    """
    ✅ Extract JWT token from Authorization header
    
    Use when processing headers manually:
        auth_header = request.headers.get("Authorization")
        token = extract_bearer_token(auth_header)
    
    Args:
        auth_header: "Authorization" header value (e.g., "Bearer <token>")
    
    Returns:
        str: Token if valid format, None if invalid
    """
    if not auth_header:
        logger.warning("⚠️  No authorization header provided")
        return None
    
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("⚠️  Invalid authorization header format")
        return None
    
    token = parts[1]
    logger.info(f"✅ Bearer token extracted: {token[:20]}...")
    return token

# ═══════════════════════════════════════════════════════════════════════════════
# 🔐 DECORATOR: Check trial status before allowing API access
# ═══════════════════════════════════════════════════════════════════════════════

def check_trial_status(func):
    """
    ✅ Decorator to check trial status on protected routes
    
    Usage:
        @router.post("/upload-and-process")
        @verify_token
        @check_trial_status  # ← Add this line
        async def upload_file(file: UploadFile, token: dict):
            ...
    
    Returns:
        - 200: User has active trial or paid subscription
        - 402: Trial expired, show paywall
        - 401: Token invalid
    """
    
    async def wrapper(*args, **kwargs):
        # Extract token from kwargs
        token = kwargs.get('token')
        
        if not token:
            logger.error("❌ No token provided to check_trial_status")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token required"
            )
        
        # Get user email from token
        user_email = token.get('email')
        
        if not user_email:
            logger.error("❌ No email in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check trial status
        trial_status, error_msg = TrialManager.check_trial_status(user_email)

        # ✅ NEW: log the decision clearly
        logger.info(f"[TRIAL] Decorator check_trial_status → {trial_status} for {user_email}")
        
        if trial_status == "ALLOWED":
            # User can proceed
            logger.info(f"✅ Trial check passed: {user_email}")
            return await func(*args, **kwargs)
        
        else:
            # Trial expired - return 402
            logger.warning(f"🔒 Trial check failed: {user_email} - {error_msg}")
            raise HTTPException(
                status_code=402,  # Payment Required
                detail=error_msg or "Trial expired. Please upgrade."
            )
    
    return wrapper

# ═══════════════════════════════════════════════════════════════════════════════
# ✅ NEW: Async wrapper for the decorator
# ═══════════════════════════════════════════════════════════════════════════════

from functools import wraps

def check_trial_status_async(func):
    """
    ✅ Async decorator to check trial status on protected routes
    
    Usage:
        @router.post("/upload-and-process")
        @verify_token
        @check_trial_status_async  # ← Add this line
        async def upload_file(file: UploadFile, token: dict):
            ...
    """
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract token from kwargs
        token = kwargs.get('token')
        
        if not token:
            logger.error("❌ No token provided to check_trial_status_async")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token required"
            )
        
        # Get user email from token
        user_email = token.get('email')
        
        if not user_email:
            logger.error("❌ No email in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check trial status
        trial_status, error_msg = TrialManager.check_trial_status(user_email)

         # ✅ NEW: log the decision clearly for async wrapper
        logger.info(f"[TRIAL] Decorator check_trial_status_async → {trial_status} for {user_email}")
        
        if trial_status == "ALLOWED":
            # User can proceed
            logger.info(f"✅ Trial check passed: {user_email}")
            return await func(*args, **kwargs)
        
        else:
            # Trial expired - return 402
            logger.warning(f"🔒 Trial check failed: {user_email} - {error_msg}")
            raise HTTPException(
                status_code=402,  # Payment Required
                detail=error_msg or "Trial expired. Please upgrade."
            )
    
    return wrapper
