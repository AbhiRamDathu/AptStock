import pandas as pd

from app.routes.forecast_routes import generate_inventory_real_from_file
from app.routes.forecast_routes import generate_actions_v2_smart
from fastapi import APIRouter, Query, HTTPException , Depends
from app.middlewares.auth_middlewares import verify_token
from app.services.database_service import db

router = APIRouter(tags=["inventory"])

@router.get("/api/inventory-alerts")
async def get_inventory_alerts(
    store: str = Query(..., description="Supermarket or store name"),
    token: dict = Depends(verify_token)
):
    try:
        sales_records = list(
            db.sales.find(
                {"store": store.strip()},
                {"_id": 0}
            )
        )

        if not sales_records:
            return {
                "store": store,
                "status": "connected",
                "data_source": "sales",
                "alerts": [],
                "message": "No sales data available."
            }

        df = pd.DataFrame(sales_records)

        if df.empty:
            return {
                "store": store,
                "status": "connected",
                "data_source": "sales",
                "alerts": [],
                "message": "No sales data available."
            }

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["quantity"] = pd.to_numeric(
            df["quantity"],
            errors="coerce"
        )

        df = df.dropna(subset=["date", "sku", "quantity"])

        if df.empty:
            return {
                "store": store,
                "status": "connected",
                "data_source": "sales",
                "alerts": [],
                "message": "No valid sales records found."
            }

        inventory = generate_inventory_real_from_file(
            df=df,
            sales_column="quantity",
            unit_cost_dict={},
            unit_price_dict={},
            current_stock_dict={},
            lead_time_dict={},
            forecasts_list=[]
        )

        priority_actions = generate_actions_v2_smart(
            inventory
        )

        return {
            "store": store,
            "status": "connected",
            "data_source": "sales",
            "alerts": priority_actions,
            "inventory": inventory,
            "message": f"Found inventory information for {len(inventory)} products."
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inventory service error: {str(e)}"
        )