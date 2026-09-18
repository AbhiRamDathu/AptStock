from fastapi import APIRouter, Query

router = APIRouter(tags=["inventory"])


@router.get("/api/inventory-alerts")
async def get_inventory_alerts(
    store: str = Query(..., description="Supermarket or store name")
):
    return {
        "store": store,
        "status": "connected",
        "alerts": [],
        "message": "Inventory alert service is ready."
    }