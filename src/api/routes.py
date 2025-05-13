"""
API routes for the Newsaroo application.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from src.api.models import NewsResponse, UserRegistration, UserResponse, UpdateTopicsRequest, NewsRequest, Article, ErrorResponse
from src.config import SERPAPI_KEY, OPENAI_API_KEY, DEFAULT_CONFIG
from ..news.search import search_news
from ..news.content import process_news_results
from ..news.summary import summarize_with_llm
from src.db.supabase_client import get_supabase_client
import logging
from datetime import datetime
from typing import List

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@router.post("/news/summarize", response_model=NewsResponse, tags=["News"])
async def summarize_news(request: NewsRequest):
    """
    Get a summary of news articles for a specific topic
    
    Parameters:
    - topic: The news topic to search for
    - time_period: Time period for news (1d to 7d, default: 1d)
    - max_articles: Number of articles to process (1-20, default: 5)
    """
    try:
        # Check API keys first
        if not SERPAPI_KEY or not OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="API keys not found. Please check your configuration."
            )

        # Search for news with custom time period
        news_results = await search_news(
            topic=request.topic,
            api_key=SERPAPI_KEY,
            time_period=request.time_period
        )
        if not news_results:
            raise HTTPException(
                status_code=404,
                detail=f"No news found for topic: {request.topic}"
            )

        # Process articles with custom limit
        processed_articles = await process_news_results(
            news_results=news_results,
            max_articles=request.max_articles
        )
        if not processed_articles:
            raise HTTPException(
                status_code=500,
                detail="Failed to process news articles"
            )

        # Generate summary
        summary = await summarize_with_llm(processed_articles, request.topic)
        if summary.startswith("Error:"):
            raise HTTPException(
                status_code=500,
                detail=summary
            )

        # Create response
        articles = [
            Article(
                title=article["title"],
                source=article["source"],
                summary=article["content"][:200] + "..."  # Short preview
            )
            for article in processed_articles
        ]

        return NewsResponse(
            topic=request.topic,
            summary=summary,
            articles=articles,
            timestamp=datetime.now().isoformat(),
            metadata={
                "time_period": request.time_period,
                "articles_found": len(articles),
                "total_results": len(news_results)
            }
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/users", response_model=UserResponse)
async def register_user(user: UserRegistration):
    """Register a new user with their topics of interest
    
    Args:
        user (UserRegistration): User registration details
        
    Returns:
        UserResponse: Registered user details
    """
    try:
        supabase = get_supabase_client()
        
        # Convert topics to JSON format
        user_data = {
            "name": user.name,
            "mobile_no": user.mobile_no,
            "topics_of_interest": user.topics_of_interest
        }
        
        # Insert data into Supabase
        result = supabase.table("newsaroo_users").insert(user_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
            
        created_user = result.data[0]
        
        return UserResponse(
            id=created_user['id'],
            name=created_user['name'],
            mobile_no=created_user['mobile_no'],
            topics_of_interest=created_user['topics_of_interest'],
            created_at=created_user['created_at']
        )
        
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error registering user: {str(e)}"
        )

@router.get("/debug-config")
async def debug_config():
    """Temporary route to debug configuration"""
    from ..config import SUPABASE_URL, SUPABASE_KEY
    return {
        "supabase_url": SUPABASE_URL,
        "supabase_key": SUPABASE_KEY and "exists" or "missing"
    }

@router.get("/user_news_summary/{mobile_no}")
async def get_user_news_summary(
    mobile_no: int = Path(
        ..., 
        description="User's mobile number",
        gt=1000000000,  # 10-digit number validation
        lt=9999999999
    )
):
    """Get personalized news summary based on user's topics of interest"""
    try:
        # 1. Get Supabase client
        supabase = get_supabase_client()
        
        # 2. Query user's topics of interest
        response = supabase.table("newsaroo_users")\
            .select("topics_of_interest, name")\
            .eq("mobile_no", mobile_no)\
            .execute()
            
        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"No user found with mobile number: {mobile_no}"
            )
            
        user_data = response.data[0]
        topics = user_data.get('topics_of_interest', [])
        user_name = user_data.get('name')
        
        if not topics:
            raise HTTPException(
                status_code=404,
                detail="No topics of interest found for this user"
            )
            
        logger.info(f"Found topics for user {user_name}: {topics}")
        
        # 3. Generate summaries for each topic
        all_summaries = []
        for topic in topics:
            # Search for news
            news_results = await search_news(topic)
            
            if news_results:
                # Process the news results
                processed_articles = await process_news_results(news_results)
                
                if processed_articles:
                    # Generate summary
                    summary = await summarize_with_llm(processed_articles, topic)
                    all_summaries.append({
                        "topic": topic,
                        "summary": summary
                    })
        
        if not all_summaries:
            return {
                "message": "No news found for any of your topics of interest",
                "user_name": user_name,
                "topics_searched": topics
            }
            
        return {
            "user_name": user_name,
            "summaries": all_summaries
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error generating news summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating news summary: {str(e)}"
        )

@router.put("/update_users_topics/{mobile_no}")
async def update_users_topics(
    request: UpdateTopicsRequest,
    mobile_no: int = Path(
        ..., 
        description="User's mobile number",
        gt=1000000000,  # 10-digit number validation
        lt=9999999999
    )
):
    """Update topics of interest for a user"""
    try:
        supabase = get_supabase_client()
        
        # First check if user exists
        user_check = supabase.table("newsaroo_users")\
            .select("id, name")\
            .eq("mobile_no", mobile_no)\
            .execute()
            
        if not user_check.data:
            raise HTTPException(
                status_code=404,
                detail=f"No user found with mobile number: {mobile_no}"
            )
            
        # Update the topics
        response = supabase.table("newsaroo_users")\
            .update({"topics_of_interest": request.topics_of_interest})\
            .eq("mobile_no", mobile_no)\
            .execute()
        
        return {
            "message": "Topics updated successfully",
            "mobile_no": mobile_no,
            "name": user_check.data[0]['name'],
            "updated_topics": request.topics_of_interest
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating topics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating topics: {str(e)}"
        ) 