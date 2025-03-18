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
    max_articles: Optional[int] = Field(
        default=3,
        description="Maximum number of articles to process",
        ge=1,  # greater than or equal to 1
        le=20,  # less than or equal to 20
        example=3
    )
    time_period: Optional[str] = Field(
        default="1d",
        description="Time period for news search (e.g., 1d, 7d)",
        pattern="^[1-7]d$",  # only allow 1d to 7d
        example="1d"
    )

class Article(BaseModel):
    """Model for processed article information"""
    title: str
    source: str
    date: str
    link: str
    snippet: str

class NewsResponse(BaseModel):
    """Response model for news summarization"""
    task_id: str = Field(..., description="Unique identifier for the task")
    status: TaskStatus = Field(..., description="Current status of the task")
    summary: Optional[str] = Field(None, description="Generated summary when completed")
    error: Optional[str] = Field(None, description="Error message if task failed")
    articles: Optional[List[Article]] = Field(
        None,
        description="List of articles used for summarization"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "summary": "1. Important development...\n2. Major announcement...\n3. Key trend...",
                "articles": [
                    {
                        "title": "Breaking News Article",
                        "source": "News Source",
                        "date": "2024-03-07",
                        "link": "https://example.com/article",
                        "snippet": "Article preview text..."
                    }
                ]
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