"""Purchases router."""

from fastapi import APIRouter, HTTPException

from models import Purchase, PurchaseResponse
from utils.database import get_driver


router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post(
    "/",
    summary="Record a purchase for a user",
    description=(
        "Create a PURCHASE relationship from a user (by mobile) to a new Purchase "
        "node with item and details. The purchase gets a unique UUID."
    ),
    response_model=PurchaseResponse,
    responses={
        200: {
            "description": "Purchase recorded successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "message": "Purchase recorded"
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def create_purchase(purchase_data: Purchase):
    """Record a purchase for a user."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                session.run(
                    "MATCH (u:User {mobile: $User_mobile}) "
                    "CREATE (u)-[:PURCHASED {item: $item, details: $details}]->(p:Purchase {id: randomUUID()})",
                    **purchase_data.dict()
                )
            return {"statuscode": 200, "status": "success", "message": "Purchase recorded"}
        finally:
            driver.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
