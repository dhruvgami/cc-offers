"""Search API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import get_db, DatabaseClient

router = APIRouter()


class SearchRequest(BaseModel):
    """Request model for hotel search"""
    location: str = Field(..., description="Location (city, address, or hotel name)")
    check_in: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    guests: int = Field(default=2, ge=1, le=10, description="Number of guests")
    discount_types: Optional[List[str]] = Field(
        default=["aarp", "aaa", "senior"],
        description="Discount types to test"
    )


class SearchResponse(BaseModel):
    """Response model for search initiation"""
    search_id: str
    status: str
    message: str


@router.post("/search", response_model=SearchResponse)
async def create_search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Initiate a new hotel discount search.

    This endpoint creates a search record and will trigger scraping tasks.
    Use the returned search_id to poll for results.
    """
    try:
        # Create database client
        db_client = DatabaseClient(db)

        # Create search record
        search = db_client.create_search(
            user_id="anonymous",  # TODO: Get from auth when implemented
            location=request.location,
            check_in=request.check_in,
            check_out=request.check_out,
            guests=request.guests,
            filters={"discount_types": request.discount_types}
        )

        # TODO: Trigger scraping tasks via Celery
        # For now, we'll just create the search record

        return SearchResponse(
            search_id=search.id,
            status="pending",
            message=f"Search initiated for {request.location}. Use /api/results/{search.id} to check progress."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create search: {str(e)}")


@router.get("/searches")
async def list_searches(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List recent searches.

    Returns the most recent searches (for debugging/testing).
    """
    try:
        from shared.models import Search

        searches = db.query(Search).order_by(Search.created_at.desc()).limit(limit).all()

        return {
            "count": len(searches),
            "searches": [
                {
                    "search_id": s.id,
                    "location": s.location,
                    "check_in": s.check_in_date,
                    "check_out": s.check_out_date,
                    "guests": s.guests,
                    "status": s.status,
                    "created_at": s.created_at.isoformat()
                }
                for s in searches
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list searches: {str(e)}")
