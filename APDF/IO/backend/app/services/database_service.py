from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from datetime import datetime
from typing import Optional
import os

from app.config import MONGODB_URI, DATABASE_NAME

# MongoDB Connection
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Collections
users_collection = db["users"]

# Create indexes
users_collection.create_index("email", unique=True)


class DatabaseService:
    
    @staticmethod
    def create_user(user_data: dict) -> Optional[str]:
        """Create new user in database"""
        try:
            user_doc = {
                "email": user_data["email"],
                "password_hash": user_data["password_hash"],
                "full_name": user_data["full_name"],
                "company_name": user_data["company_name"],
                "created_at": datetime.utcnow(),
                "is_verified": False,
                "refresh_tokens": []
            }
            result = users_collection.insert_one(user_doc)
            return str(result.inserted_id)
        except DuplicateKeyError:
            return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[dict]:
        """Fetch user by email"""
        user = users_collection.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
            del user["_id"]
        return user

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[dict]:
        """Fetch user by ID"""
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                del user["_id"]
            return user
        except:
            return None

    @staticmethod
    def store_refresh_token(user_id: str, refresh_token: str) -> bool:
        """Store refresh token for session management"""
        try:
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"refresh_tokens": refresh_token}}
            )
            return True
        except:
            return False

    @staticmethod
    def verify_refresh_token(user_id: str, refresh_token: str) -> bool:
        """Check if refresh token exists"""
        try:
            user = users_collection.find_one(
                {"_id": ObjectId(user_id), "refresh_tokens": refresh_token}
            )
            return user is not None
        except:
            return False

    @staticmethod
    def remove_refresh_token(user_id: str, refresh_token: str) -> bool:
        """Remove refresh token (logout)"""
        try:
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"refresh_tokens": refresh_token}}
            )
            return True
        except:
            return False

    @staticmethod
    def set_reset_otp(email: str, otp_code: str, expiry: datetime) -> bool:
        """Store OTP and expiry on user document"""
        try:
            result = users_collection.update_one(
                {"email": email},
                {"$set": {
                    "reset_otp": otp_code,
                    "reset_otp_expiry": expiry,
                    "reset_otp_used": False
                }}
            )
            print(f"[DEBUG] OTP stored for {email}: {otp_code} (modified: {result.modified_count})")
            return True
        except Exception as e:
            print(f"[ERROR] Error storing OTP: {e}")
            return False

    @staticmethod
    def mark_reset_otp_used(email: str) -> bool:
        """Mark OTP as used"""
        try:
            result = users_collection.update_one(
                {"email": email},
                {"$set": {"reset_otp_used": True}}
            )
            print(f"[DEBUG] OTP marked used for {email}")
            return True
        except Exception as e:
            print(f"[ERROR] Error marking OTP used: {e}")
            return False

    @staticmethod
    def update_user_password(email: str, password_hash: str) -> bool:
        """Update user password"""
        try:
            result = users_collection.update_one(
                {"email": email},
                {"$set": {"password_hash": password_hash}}
            )
            print(f"[DEBUG] Password updated for {email}")
            return True
        except Exception as e:
            print(f"[ERROR] Error updating password: {e}")
            return False
