import os
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
import pathlib

from datetime import datetime, timedelta


# ========== SETUP ==========
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ========== ROUTE IMPORTS ==========
from app.routes.auth_routes import router as auth_router
from app.routes.forecast_routes import router as forecast_router  # ✅ NEW


app.include_router(auth_router)
app.include_router(forecast_router)  # ✅ NEW

app.include_router(auth_router, prefix="/auth")

# ========== ROOT ENDPOINTS ==========
@app.get("/")
async def root():
    return {
        "message": "🚀 ForecastAI Pro API",
        "version": "2.0.0",
        "status": "✅ Running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return { "status": "online",
        "mode": "BACKEND-DRIVEN (TRUE ONLINE)",  # ✅ Changed
        "timestamp": datetime.utcnow()
        }

# ========== STARTUP/SHUTDOWN ==========
@app.on_event("startup")
async def startup():
    logger.info("✅ ForecastAI Pro API Started")

@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()
    logger.info("✅ MongoDB connection closed")

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
