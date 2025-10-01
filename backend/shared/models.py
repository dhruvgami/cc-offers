"""Database models using SQLAlchemy ORM"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship
import uuid


Base = declarative_base()


def generate_uuid():
    """Generate UUID as string"""
    return str(uuid.uuid4())


class Hotel(Base):
    """Hotel property information"""
    __tablename__ = "hotels"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, index=True)
    chain = Column(String, nullable=False, index=True)
    address = Column(String)
    city = Column(String, index=True)
    state = Column(String)
    country = Column(String, default="USA")
    latitude = Column(Float)
    longitude = Column(Float)
    star_rating = Column(Float)
    amenities = Column(JSON)  # Store as JSON: ["wifi", "parking", "pool"]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    results = relationship("Result", back_populates="hotel")

    # Composite index for common queries
    __table_args__ = (
        Index('idx_chain_city', 'chain', 'city'),
    )

    def __repr__(self):
        return f"<Hotel(name='{self.name}', chain='{self.chain}', city='{self.city}')>"


class Search(Base):
    """Search request record"""
    __tablename__ = "searches"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, index=True, default="anonymous")  # For future user auth
    location = Column(String, nullable=False)
    check_in_date = Column(String, nullable=False)  # Format: YYYY-MM-DD
    check_out_date = Column(String, nullable=False)  # Format: YYYY-MM-DD
    guests = Column(Integer, default=2)
    filters = Column(JSON)  # Store search filters: {"discount_types": ["aarp", "aaa"]}
    status = Column(String, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)

    # Relationships
    results = relationship("Result", back_populates="search", cascade="all, delete-orphan")

    # Index for user queries
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    )

    def __repr__(self):
        return f"<Search(id='{self.id}', location='{self.location}', status='{self.status}')>"


class Result(Base):
    """Scraping result for a hotel + discount combination"""
    __tablename__ = "results"

    id = Column(String, primary_key=True, default=generate_uuid)
    search_id = Column(String, ForeignKey("searches.id"), nullable=False, index=True)
    hotel_id = Column(String, ForeignKey("hotels.id"), nullable=False, index=True)
    discount_type = Column(String, nullable=False)  # none, aarp, aaa, senior, military, etc.
    original_price = Column(Float)
    discounted_price = Column(Float)
    taxes = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    total_price = Column(Float)
    currency = Column(String, default="USD")
    available = Column(Boolean, default=True)
    raw_data = Column(JSON)  # Store additional scraped data
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    search = relationship("Search", back_populates="results")
    hotel = relationship("Hotel", back_populates="results")

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_search_scraped', 'search_id', 'scraped_at'),
        Index('idx_hotel_scraped', 'hotel_id', 'scraped_at'),
        Index('idx_discount_type', 'discount_type'),
    )

    def __repr__(self):
        return f"<Result(hotel_id='{self.hotel_id}', discount='{self.discount_type}', price=${self.total_price})>"


class DiscountCode(Base):
    """Discount codes for hotel chains"""
    __tablename__ = "discount_codes"

    id = Column(String, primary_key=True, default=generate_uuid)
    code = Column(String, nullable=False)
    type = Column(String, nullable=False)  # aarp, aaa, senior, military, corporate
    hotel_chain = Column(String, nullable=False, index=True)
    requirements = Column(String)  # Description of requirements (e.g., "Age 50+")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_chain_type', 'hotel_chain', 'type'),
    )

    def __repr__(self):
        return f"<DiscountCode(chain='{self.hotel_chain}', type='{self.type}', code='{self.code}')>"


class User(Base):
    """User account (for future use with authentication)"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    memberships = Column(JSON)  # Store membership info: {"aarp": "12345", "aaa": "67890"}
    preferences = Column(JSON)  # User preferences for searches
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(email='{self.email}')>"
