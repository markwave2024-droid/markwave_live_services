"""Products router."""

from fastapi import APIRouter, HTTPException

from models import ProductResponse, ProductListResponse
from utils.database import get_driver


router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "/{product_id}",
    summary="Get product details",
    description="Fetch a single BUFFALO product node by its id from the Neo4j database.",
    response_model=ProductResponse,
    responses={
        200: {
            "description": "Product details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "product": {
                            "id": "buffalo-001",
                            "name": "Premium Buffalo Milk",
                            "price": 80,
                            "description": "Fresh organic buffalo milk",
                            "available": True
                        }
                    }
                }
            }
        },
        404: {"description": "Product not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_product_details(product_id: str):
    """Return product details for a given product id from Neo4j database."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (n:BUFFALO) WHERE n.id=$product_id RETURN n", product_id=product_id)
                record = result.single()
                
                if not record:
                    raise HTTPException(status_code=404, detail="Product not found")
                
                product_node = record["n"]
                product_data = dict(product_node)
                
                return {"statuscode": 200, "status": "success", "product": product_data}
        finally:
            driver.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "",
    summary="List all buffalo products",
    description="Return all PRODUCT:BUFFALO nodes stored in Neo4j database.",
    response_model=ProductListResponse,
    responses={
        200: {
            "description": "List of all buffalo products",
            "content": {
                "application/json": {
                    "example": {
                        "statuscode": 200,
                        "status": "success",
                        "products": [
                            {
                                "id": "buffalo-001",
                                "name": "Premium Buffalo Milk",
                                "price": 80,
                                "available": True
                            },
                            {
                                "id": "buffalo-002",
                                "name": "Buffalo Ghee",
                                "price": 500,
                                "available": True
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def get_products():
    """Return all buffalo products stored in Neo4j as PRODUCT:BUFFALO nodes."""
    try:
        driver = get_driver()
        try:
            with driver.session() as session:
                result = session.run("MATCH (p:PRODUCT:BUFFALO) RETURN p")
                products = [dict(record["p"]) for record in result]
            return {"statuscode": 200, "status": "success", "products": products}
        finally:
            driver.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
