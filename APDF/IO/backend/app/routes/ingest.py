from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
import io
from app.config import db

router = APIRouter(prefix="/upload", tags=["ingest"])


@router.post("/sales")
async def upload_sales(file: UploadFile = File(...)):
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content), parse_dates=["date"])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    records = df.to_dict("records")
    if not records:
        raise HTTPException(status_code=400, detail="CSV contains no records")
    await db.sales.insert_many(records)
    return {"inserted": len(records)}
