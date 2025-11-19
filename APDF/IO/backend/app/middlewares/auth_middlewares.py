# ✅ COMPLETE: app/middleware/auth.py
# JWT Authentication Middleware for FastAPI

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime
import logging
from typing import Optional, Dict

from app.config import JWT_SECRET, JWT_ALGORITHM

# ✅ Setup logging
logger = logging.getLogger(__name__)

# ✅ Security scheme for API endpoints
security = HTTPBearer()

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
