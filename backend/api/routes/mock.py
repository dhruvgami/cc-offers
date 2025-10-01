"""Mock data endpoints for frontend testing"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.database import get_db, DatabaseClient

router = APIRouter()


@router.post("/mock/search")
async def create_mock_search(db: Session = Depends(get_db)):
    """
    Create a mock search with sample data for testing.
    This generates fake results immediately.
    """
    db_client = DatabaseClient(db)

    # Create search
    search = db_client.create_search(
        user_id="demo",
        location="New York, NY",
        check_in=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        check_out=(datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d"),
        guests=2,
        filters={"discount_types": ["aarp", "aaa", "senior"]}
    )

    # Get sample hotels
    from shared.models import Hotel
    hotels = db.query(Hotel).all()

    if not hotels:
        # Create sample hotels if they don't exist
        hotels = [
            db_client.create_hotel(
                name="Marriott Times Square",
                chain="Marriott",
                city="New York",
                state="NY",
                address="1535 Broadway, New York, NY 10036"
            ),
            db_client.create_hotel(
                name="Hilton Midtown",
                chain="Hilton",
                city="New York",
                state="NY",
                address="1335 Avenue of the Americas, New York, NY 10019"
            ),
            db_client.create_hotel(
                name="Holiday Inn Times Square",
                chain="IHG",
                city="New York",
                state="NY",
                address="585 8th Ave, New York, NY 10018"
            )
        ]

    # Generate mock results for each hotel and discount type
    discount_types = ["none", "aarp", "aaa", "senior"]

    for hotel in hotels:
        base_price = 250.0 if "Marriott" in hotel.name else 220.0 if "Hilton" in hotel.name else 180.0

        for discount_type in discount_types:
            # Calculate discount
            discount = 0.0
            if discount_type == "aarp":
                discount = 0.10  # 10% off
            elif discount_type == "aaa":
                discount = 0.08  # 8% off
            elif discount_type == "senior":
                discount = 0.12  # 12% off

            original_price = base_price
            discounted_price = base_price * (1 - discount) if discount > 0 else base_price
            taxes = discounted_price * 0.15  # 15% tax
            fees = 25.0  # Flat fee
            total = discounted_price + taxes + fees

            # Create result
            db_client.create_result(
                search_id=search.id,
                hotel_id=hotel.id,
                discount_type=discount_type,
                prices={
                    "original": original_price,
                    "discounted": discounted_price,
                    "taxes": taxes,
                    "fees": fees,
                    "total": total,
                    "currency": "USD"
                },
                available=True
            )

    # Update search status to completed
    db_client.update_search_status(search.id, "completed")

    return {
        "search_id": search.id,
        "status": "completed",
        "message": f"Mock search created with {len(hotels) * len(discount_types)} results"
    }
