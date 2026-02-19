import os
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import pathlib
from fastapi import APIRouter, Depends
from app.services.database_service import DatabaseService

from datetime import datetime, timedelta

from app.routes import forecast_routes, auth_routes


# ========== SETUP ==========
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a router for admin endpoints
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

# ========== MONGODB ==========
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "apdf_io_mongo")

mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = mongo_client[DATABASE_NAME]
logger.info(f"✅ MongoDB Connected: {DATABASE_NAME}")

# ========== FASTAPI APP ==========
app = FastAPI(
    title="ForecastAI Pro API",
    description="AI-Powered Demand Forecasting with OTP Password Reset",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========== CORS MIDDLEWARE ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ROUTES ==========
app.include_router(auth_routes.router, prefix="/auth", tags=["authentication"])
app.include_router(forecast_routes.router, prefix="/api/forecast", tags=["forecasting"])
app.include_router(forecast_routes.router)


# ========== ROOT ENDPOINTS ==========

# ========== STARTUP/SHUTDOWN ==========
@app.on_event("startup")
async def startup():
    logger.info("✅ ForecastAI Pro API Started")

@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()
    logger.info("✅ MongoDB connection closed")

@app.get("/")
def root():
    return {
        "message": "ForecastAI Pro API Running",
        "status": "operational",
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ForecastAI Pro"}

@admin_router.get("/health")
async def system_health():
    """
    Simple health check - can be called by monitoring tools
    Returns database status and stats
    """
    db_health = DatabaseService.check_database_health()
    db_stats = DatabaseService.get_database_stats()
    
    return {
        "service": "ForecastAI Pro",
        "timestamp": datetime.utcnow().isoformat(),
        "database": {
            "health": db_health,
            "stats": db_stats
        }
    }

@admin_router.get("/user-activity/{user_id}")
async def get_user_activity(user_id: str, days: int = 7):
    """
    Get user's activity log for monitoring/debugging
    """
    activity = DatabaseService.get_user_activity_history(user_id, days=days)
    return {
        "user_id": user_id,
        "activity_count": len(activity),
        "activities": activity
    }

# Register router in your FastAPI app
app.include_router(admin_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)

