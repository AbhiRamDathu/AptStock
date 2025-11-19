from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class FileAnalysis(BaseModel):
    user_id: str
    filename: str
    file_data: str
    total_records: int
    unique_skus: int
    date_range: str
    total_units: float
    processed_at: datetime

class ForecastResult(BaseModel):
    sku: str
    item_name: str
    forecast: List[Dict[str, Any]]
    r2_score: float

class InventoryRec(BaseModel):
    sku: str
    item_name: str
    current_stock: int
    recommended_stock: int
    safety_stock: int
    reorder_point: int

class ROIMetrics(BaseModel):
    current_revenue: int
    projected_increase: int
    inventory_cost_savings: int
    improvement_percent: int
    stockout_reduction: int
    net_roi: int
