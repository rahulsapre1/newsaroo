"""
Pydantic models for request and response validation in the Newsaroo API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    """Enum for possible task statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class NewsRequest(BaseModel):
    """Request model for news summarization"""
    topic: str = Field(
        ...,
        description="The news topic to search for",
        example="artificial intelligence"
    )
    time_period: str = Field(
        default="1d",
        description="Time period for news search (e.g., 1d, 7d)",
        pattern="^[1-7]d$",  # only allow 1d to 7d
        example="1d"
    )
    max_articles: int = Field(
        default=5,
        description="Maximum number of articles to process",
        ge=1,  # greater than or equal to 1
        le=20,  # less than or equal to 20
        example=3
    )

class Article(BaseModel):
    """Model for processed article information"""
    title: str
    source: str
    summary: str

class NewsResponse(BaseModel):
    """Response model for news summarization"""
    topic: str
    summary: str
    articles: List[Article]
    timestamp: str
    metadata: dict = Field(
        default_factory=dict,
        description="Additional information about the search"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "artificial intelligence",
                "summary": "1. Important development...\n2. Major announcement...\n3. Key trend...",
                "articles": [
                    {
                        "title": "Breaking News Article",
                        "source": "News Source",
                        "summary": "Article preview text..."
                    }
                ],
                "timestamp": "2024-03-07T12:00:00"
            }
        }

class UserRegistration(BaseModel):
    """Request model for user registration"""
    name: str = Field(..., description="User's name")
    mobile_no: int = Field(
        ..., 
        description="User's mobile number",
        gt=1000000000,  # 10-digit number validation
        lt=9999999999
    )
    topics_of_interest: List[str] = Field(
        ...,
        description="List of topics the user is interested in",
        min_items=1
    )

class UserResponse(BaseModel):
    """Response model for user registration"""
    id: int
    name: str
    mobile_no: int
    topics_of_interest: List[str]
    created_at: datetime

class UpdateTopicsRequest(BaseModel):
    """Request model for updating topics of interest"""
    topics_of_interest: List[str] = Field(
        ...,
        description="New list of topics of interest",
        min_items=1,
        example=["technology", "sports", "politics"]
    )

class ErrorResponse(BaseModel):
    detail: str
    status_code: int 