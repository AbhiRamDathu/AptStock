from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from datetime import datetime, timedelta
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
        """Create new user in database WITH 14-DAY FREE TRIAL"""
        try:
            # Calculate trial end date (14 days from now)
            trial_start = datetime.utcnow()
            trial_end = trial_start + timedelta(days=14)
        
            user_doc = {
                "email": user_data["email"],
                "password_hash": user_data["password_hash"],
                "full_name": user_data["full_name"],
                "company_name": user_data["company_name"],
            
                # ✅ NEW: TRIAL FIELDS
                "trial_status": "ACTIVE",  # ACTIVE | EXPIRED | PAID
                "trial_start_date": trial_start,
                "trial_end_date": trial_end,
                "free_uploads_remaining": 10,
                "max_free_uploads": 10,
            
                # ✅ NEW: SUBSCRIPTION FIELDS
                "subscription_tier": "FREE",  # FREE | STARTER | PRO | ENTERPRISE
                "subscription_end_date": None,  # Null until they pay
            
                # Keep existing fields
                "created_at": datetime.utcnow(),
                "is_verified": False,
                "refresh_tokens": []
            }
        
            result = users_collection.insert_one(user_doc)
            print(f"[✅ TRIAL] User {user_data['email']} created with 14-day trial (ends {trial_end.strftime('%Y-%m-%d')})")
            return str(result.inserted_id)
        
        except DuplicateKeyError:
            print(f"[⚠️] Email already registered: {user_data['email']}")
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
    def update_trial_status(email: str, status: str) -> bool:
        """Update user's trial status"""
        try:
            result = users_collection.update_one(
                {"email": email},
                {"$set": {"trial_status": status}}
            )
            print(f"[✅] Trial status updated for {email}: {status}")
            return True
        except Exception as e:
            print(f"[❌] Error updating trial status: {e}")
            return False

    @staticmethod
    def update_subscription(email: str, tier: str, end_date: datetime = None) -> bool:
        """Update user's subscription tier"""
        try:
            update_data = {"subscription_tier": tier}
            if end_date:
                update_data["subscription_end_date"] = end_date
        
            result = users_collection.update_one(
                {"email": email},
                {"$set": update_data}
            )
            print(f"[✅] Subscription updated for {email}: {tier}")
            return True
        except Exception as e:
            print(f"[❌] Error updating subscription: {e}")
            return False

    @staticmethod
    def get_trial_info(user_id: str) -> dict:
        """Get user's trial and subscription info"""
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {}
        
            trial_info = {
                "trial_status": user.get("trial_status", "ACTIVE"),
                "trial_start_date": user.get("trial_start_date"),
                "trial_end_date": user.get("trial_end_date"),
                "trial_days_remaining": 0,
                "subscription_tier": user.get("subscription_tier", "FREE"),
                "subscription_end_date": user.get("subscription_end_date"),
                "free_uploads_remaining": user.get("free_uploads_remaining", 10)
            }
        
            # Calculate days remaining
            if user.get("trial_status") == "ACTIVE" and user.get("trial_end_date"):
                days_remaining = (user["trial_end_date"] - datetime.utcnow()).days
                trial_info["trial_days_remaining"] = max(0, days_remaining)
        
            return trial_info
        except Exception as e:
            print(f"[❌] Error getting trial info: {e}")
            return {}

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

    @staticmethod
    def log_user_action(
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        status: str = "success"
    ) -> bool:
        """Log user actions for audit trail"""
        try:
            audit_logs = db["audit_logs"]
            
            log_entry = {
                "user_id": ObjectId(user_id) if user_id else None,
                "action": action,  # "login", "logout", "upload_file", "export_data"
                "resource_type": resource_type,  # "file", "forecast", "user"
                "resource_id": resource_id,
                "details": details or {},
                "status": status,
                "created_at": datetime.utcnow(),
            }
            
            audit_logs.insert_one(log_entry)
            return True
        except Exception as e:
            print(f"[ERROR] Could not log action: {e}")
            return False

    @staticmethod
    def get_user_activity_history(user_id: str, days: int = 7) -> list:
        """Get user's recent activity"""
        try:
            audit_logs = db["audit_logs"]
            from_date = datetime.utcnow() - timedelta(days=days)
            
            logs = list(
                audit_logs.find({
                    "user_id": ObjectId(user_id),
                    "created_at": {"$gte": from_date}
                }).sort("created_at", -1).limit(50)
            )
            
            return [
                {
                    **log,
                    "_id": str(log["_id"]),
                    "user_id": str(log["user_id"]),
                    "created_at": log["created_at"].isoformat()
                }
                for log in logs
            ]
        except Exception as e:
            print(f"[ERROR] Could not fetch activity: {e}")
            return []

    @staticmethod
    def get_database_stats() -> dict:
        """Get database size and collection info"""
        try:
            admin_db = client.admin
            stats = admin_db.command('dbStats')
            
            return {
                "database_size_mb": round(stats['dataSize'] / (1024 * 1024), 2),
                "storage_size_mb": round(stats['storageSize'] / (1024 * 1024), 2),
                "collections": stats['collections'],
                "total_documents": stats['objects'],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"[ERROR] Could not get DB stats: {e}")
            return {}

    @staticmethod
    def check_database_health() -> dict:
        """Quick health check"""
        try:
            admin_db = client.admin
            admin_db.command('ping')
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        
    @staticmethod
    def invalidate_refresh_tokens(user_email: str) -> bool:
        """Invalidate ALL refresh tokens for user on logout"""
        try:
            from datetime import datetime
        
            result = users_collection.update_one(
                {"email": user_email},
                {
                    "$set": {
                        "refresh_tokens": [],  # Clear all tokens
                        "tokens_invalidated_at": datetime.utcnow()
                    }
                }
            )
        
            if result.modified_count > 0:
                print(f"✅ Refresh tokens invalidated for {user_email}")
                return True
            else:
                print(f"⚠️  User not found: {user_email}")
                return False
            
        except Exception as e:
            print(f"[ERROR] Failed to invalidate tokens: {e}")
            return False
    