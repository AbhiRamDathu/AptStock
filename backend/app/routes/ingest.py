from fastapi import APIRouter, UploadFile, File, HTTPException, Form

import pandas as pd
import io

from app.services.database_service import db

router = APIRouter(prefix="/upload", tags=["ingest"])


@router.post("/sales")
async def upload_sales(
    file: UploadFile = File(...),
    store: str = Form(...)
):
    content = await file.read()

    try:
        df = pd.read_csv(
            io.BytesIO(content),
            parse_dates=["date"]
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV format"
        )

    records = df.to_dict("records")

    if not records:
        raise HTTPException(
            status_code=400,
            detail="CSV contains no records"
        )

    # Attach store ownership to every sales record.
    for record in records:
        record["store"] = store.strip()

    db.sales.insert_many(records)

    return {
        "inserted": len(records),
        "store": store.strip()
    }