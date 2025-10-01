"""Results API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import get_db, DatabaseClient
from shared.models import Search, Result, Hotel

router = APIRouter()


class ResultItem(BaseModel):
    """Single result item"""
    result_id: str
    hotel_name: str
    hotel_chain: str
    discount_type: str
    original_price: Optional[float]
    discounted_price: Optional[float]
    taxes: float
    fees: float
    total_price: Optional[float]
    currency: str
    available: bool
    scraped_at: str


class ResultsResponse(BaseModel):
    """Response model for search results"""
    search_id: str
    status: str
    location: str
    check_in: str
    check_out: str
    guests: int
    result_count: int
    results: List[ResultItem]


@router.get("/results/{search_id}", response_model=ResultsResponse)
async def get_results(
    search_id: str,
    db: Session = Depends(get_db)
):
    """
    Get results for a specific search.

    Returns all scraped results for the given search_id.
    """
    try:
        db_client = DatabaseClient(db)

        # Get search record
        search = db_client.get_search(search_id)
        if not search:
            raise HTTPException(status_code=404, detail=f"Search {search_id} not found")

        # Get results
        results = db_client.get_results_by_search(search_id)

        # Format results with hotel information
        formatted_results = []
        for result in results:
            # Get hotel info
            hotel = db.query(Hotel).filter(Hotel.id == result.hotel_id).first()

            formatted_results.append(
                ResultItem(
                    result_id=result.id,
                    hotel_name=hotel.name if hotel else "Unknown",
                    hotel_chain=hotel.chain if hotel else "Unknown",
                    discount_type=result.discount_type,
                    original_price=result.original_price,
                    discounted_price=result.discounted_price,
                    taxes=result.taxes or 0.0,
                    fees=result.fees or 0.0,
                    total_price=result.total_price,
                    currency=result.currency,
                    available=result.available,
                    scraped_at=result.scraped_at.isoformat()
                )
            )

        return ResultsResponse(
            search_id=search.id,
            status=search.status,
            location=search.location,
            check_in=search.check_in_date,
            check_out=search.check_out_date,
            guests=search.guests,
            result_count=len(formatted_results),
            results=formatted_results
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")


@router.get("/results/{search_id}/summary")
async def get_results_summary(
    search_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a summary of results grouped by hotel and discount type.

    Returns statistics and best deals.
    """
    try:
        db_client = DatabaseClient(db)

        # Get search record
        search = db_client.get_search(search_id)
        if not search:
            raise HTTPException(status_code=404, detail=f"Search {search_id} not found")

        # Get results
        results = db_client.get_results_by_search(search_id)

        if not results:
            return {
                "search_id": search_id,
                "status": search.status,
                "message": "No results available yet"
            }

        # Group by hotel
        by_hotel = {}
        best_deal = None
        best_price = float('inf')

        for result in results:
            hotel = db.query(Hotel).filter(Hotel.id == result.hotel_id).first()
            hotel_key = hotel.name if hotel else result.hotel_id

            if hotel_key not in by_hotel:
                by_hotel[hotel_key] = []

            by_hotel[hotel_key].append({
                "discount_type": result.discount_type,
                "total_price": result.total_price,
                "available": result.available
            })

            # Track best deal
            if result.available and result.total_price and result.total_price < best_price:
                best_price = result.total_price
                best_deal = {
                    "hotel": hotel_key,
                    "discount_type": result.discount_type,
                    "price": result.total_price
                }

        return {
            "search_id": search_id,
            "status": search.status,
            "total_results": len(results),
            "hotels_compared": len(by_hotel),
            "best_deal": best_deal,
            "by_hotel": by_hotel
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")
