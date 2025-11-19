from fastapi import APIRouter, HTTPException
from datetime import date
from app.config import db
from app.models import HistoricalRequest, HistoricalResponseItem
from app.services.preprocess import preprocess_sales

router = APIRouter(prefix="", tags=["metadata"])


@router.post("/historical", response_model=list[HistoricalResponseItem])
async def get_historical(req: HistoricalRequest):
    if not req.skus:
        raise HTTPException(400, "No SKUs provided")
    query = {"sku": {"$in": req.skus}, "store": req.store, "date": {"$gte": req.from_date, "$lte": req.to_date}}
    docs = await db.sales.find(query).to_list(None)
    return [HistoricalResponseItem(**doc) for doc in docs]
