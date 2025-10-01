"""Database connection and session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os

from .config import settings
from .models import Base


# Create database engine
# For SQLite: sqlite:///./data/travel_discounts.db
# For PostgreSQL: postgresql://user:password@localhost:5432/travel_discounts
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.environment == "development"  # Log SQL queries in development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables"""
    # Ensure data directory exists for SQLite
    if "sqlite" in settings.database_url:
        db_path = settings.database_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path) if "/" in db_path else ".", exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {settings.database_url}")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Use this with FastAPI's Depends() for automatic session management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session.
    Use this for non-FastAPI code (e.g., Celery tasks, scripts).

    Example:
        with get_db_context() as db:
            hotel = db.query(Hotel).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class DatabaseClient:
    """Database client with common operations"""

    def __init__(self, db: Session):
        self.db = db

    # Search operations
    def create_search(self, user_id: str, location: str, check_in: str,
                     check_out: str, guests: int, filters: dict = None):
        """Create a new search record"""
        from .models import Search

        search = Search(
            user_id=user_id or "anonymous",
            location=location,
            check_in_date=check_in,
            check_out_date=check_out,
            guests=guests,
            filters=filters or {},
            status="pending"
        )
        self.db.add(search)
        self.db.commit()
        self.db.refresh(search)
        return search

    def get_search(self, search_id: str):
        """Get search by ID"""
        from .models import Search
        return self.db.query(Search).filter(Search.id == search_id).first()

    def update_search_status(self, search_id: str, status: str):
        """Update search status"""
        from .models import Search
        from datetime import datetime

        search = self.get_search(search_id)
        if search:
            search.status = status
            if status == "completed":
                search.completed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(search)
        return search

    # Result operations
    def create_result(self, search_id: str, hotel_id: str, discount_type: str,
                     prices: dict, available: bool = True):
        """Create a new result record"""
        from .models import Result

        result = Result(
            search_id=search_id,
            hotel_id=hotel_id,
            discount_type=discount_type,
            original_price=prices.get("original"),
            discounted_price=prices.get("discounted"),
            taxes=prices.get("taxes", 0.0),
            fees=prices.get("fees", 0.0),
            total_price=prices.get("total"),
            currency=prices.get("currency", "USD"),
            available=available,
            raw_data=prices.get("raw_data")
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_results_by_search(self, search_id: str):
        """Get all results for a search"""
        from .models import Result
        return self.db.query(Result).filter(Result.search_id == search_id).all()

    # Hotel operations
    def create_hotel(self, name: str, chain: str, **kwargs):
        """Create a new hotel record"""
        from .models import Hotel

        hotel = Hotel(
            name=name,
            chain=chain,
            **kwargs
        )
        self.db.add(hotel)
        self.db.commit()
        self.db.refresh(hotel)
        return hotel

    def get_hotel_by_name_city(self, name: str, city: str):
        """Find hotel by name and city"""
        from .models import Hotel
        return self.db.query(Hotel).filter(
            Hotel.name == name,
            Hotel.city == city
        ).first()

    def get_hotels_by_chain_city(self, chain: str, city: str):
        """Get hotels by chain and city"""
        from .models import Hotel
        return self.db.query(Hotel).filter(
            Hotel.chain == chain,
            Hotel.city == city
        ).all()

    # Discount code operations
    def get_discount_codes(self, hotel_chain: str, discount_type: str = None):
        """Get discount codes for a hotel chain"""
        from .models import DiscountCode

        query = self.db.query(DiscountCode).filter(
            DiscountCode.hotel_chain == hotel_chain,
            DiscountCode.active == True
        )

        if discount_type:
            query = query.filter(DiscountCode.type == discount_type)

        return query.all()

    def create_discount_code(self, code: str, type: str, hotel_chain: str, **kwargs):
        """Create a new discount code"""
        from .models import DiscountCode

        discount = DiscountCode(
            code=code,
            type=type,
            hotel_chain=hotel_chain,
            **kwargs
        )
        self.db.add(discount)
        self.db.commit()
        self.db.refresh(discount)
        return discount
