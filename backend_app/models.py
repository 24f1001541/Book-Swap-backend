"""
Database and API models
SQLAlchemy models for database tables
Pydantic models for API request/response validation
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base
from pydantic import BaseModel, Field
from typing import Optional


# ============= SQLAlchemy Models (Database) =============

class Book(Base):
    """
    Book table in database
    Stores book metadata and references to S3 images
    """
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=False)
    user_id = Column(String(255), nullable=False, index=True)  # From Cognito
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', author='{self.author}')>"


# ============= Pydantic Models (API) =============

class BookCreate(BaseModel):
    """
    Schema for creating a new book
    Used for API request validation
    """
    title: str = Field(..., min_length=1, max_length=255, description="Book title")
    author: str = Field(..., min_length=1, max_length=255, description="Author name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald"
            }
        }


class BookResponse(BaseModel):
    """
    Schema for book response
    Used for API response serialization
    """
    id: int
    title: str
    author: str
    image_url: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows converting SQLAlchemy model to Pydantic
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "image_url": "https://bookswap-images.s3.amazonaws.com/uuid-image.jpg",
                "user_id": "cognito-user-sub",
                "created_at": "2024-11-05T10:30:00"
            }
        }