"""
API routes for the Newsaroo application.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Depends
from src.api.models import NewsResponse, UserRegistration, UserResponse, UpdateTopicsRequest, NewsRequest, Article, ErrorResponse, UserNewsSummaryResponse
from src.config import SERPAPI_KEY, OPENAI_API_KEY, DEFAULT_CONFIG, SUPABASE_API_URL, SUPABASE_API_KEY
from ..news.search import search_news
from ..news.content import process_news_results
from ..news.summary import summarize_with_llm
from src.db.supabase_client import get_supabase_client, SupabaseManager
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
                source_name=article["source"]["name"] if isinstance(article["source"], dict) else str(article["source"]),
                source_details=article["source"] if isinstance(article["source"], dict) else {},
                summary=article.get("snippet") or article.get("description") or "No preview available"
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
    """Register a new user with their topics of interest"""
    try:
        supabase = get_supabase_client()
        
        # Check if user already exists
        existing_user = await supabase.get_user(user.mobile_number)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"User with mobile number {user.mobile_number} already exists"
            )
        
        # Prepare user data
        user_data = {
            "mobile_number": user.mobile_number,
            "topics_of_interest": user.topics_of_interest,
            "created_at": datetime.now().isoformat()
        }
        
        # Insert user
        created_user = await supabase.insert_user(user_data)
        
        return UserResponse(
            id=created_user['id'],
            mobile_number=created_user['mobile_number'],
            topics_of_interest=created_user['topics_of_interest'],
            created_at=created_user['created_at']
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error registering user: {str(e)}"
        )

@router.get("/debug/config")
async def debug_config():
    """Debug endpoint to check configuration"""
    return {
        "supabase_url": SUPABASE_API_URL and "present" or "missing",
        "supabase_key": SUPABASE_API_KEY and "present" or "missing",
        "supabase_key_length": SUPABASE_API_KEY and len(SUPABASE_API_KEY) or 0,
        "timestamp": datetime.now().isoformat()
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
            logger.info(f"Searching for news on topic: {topic}")
            # Search for news with enhanced content fetching
            news_results = await search_news(topic)
            
            if news_results:
                # Check if we got enhanced content
                articles_with_full_content = [article for article in news_results if "full_content" in article]
                logger.info(f"Topic '{topic}': Found {len(articles_with_full_content)} articles with full content out of {len(news_results)} total")
                
                # Process the news results
                processed_articles = await process_news_results(news_results)
                
                if processed_articles:
                    # Calculate average content length for logging
                    avg_content_length = sum(len(article["content"]) for article in processed_articles) / len(processed_articles)
                    logger.info(f"Topic '{topic}': Average content length: {avg_content_length:.2f} characters")
                    
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

@router.get("/users/{mobile}/summaries", response_model=UserNewsSummaryResponse, tags=["Users"])
async def get_user_news_summaries(
    mobile: str = Path(
        ..., 
        description="User's mobile number",
        regex="^[0-9]{10}$"  # Ensure 10-digit mobile number
    )
):
    """Get news summaries for user's topics of interest"""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Get user's topics
        user = await supabase.get_user(mobile)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"No user found with mobile number: {mobile}"
            )
        
        topics = user.get('topics_of_interest', [])
        if not topics:
            raise HTTPException(
                status_code=404,
                detail="No topics of interest found for this user"
            )
        
        logger.info(f"Generating summaries for user with mobile {mobile} and topics: {topics}")
        
        # Generate summaries for each topic
        summaries = []
        for topic in topics:
            # Search for news with enhanced content fetching
            logger.info(f"Searching for news on topic: {topic}")
            news_results = await search_news(topic)
            
            if news_results:
                # Check if we got enhanced content
                articles_with_full_content = [article for article in news_results if "full_content" in article]
                logger.info(f"Topic '{topic}': Found {len(articles_with_full_content)} articles with full content out of {len(news_results)} total")
                
                # Process the news results
                processed_articles = await process_news_results(news_results)
                
                if processed_articles:
                    # Calculate average content length for logging
                    avg_content_length = sum(len(article["content"]) for article in processed_articles) / len(processed_articles)
                    logger.info(f"Topic '{topic}': Average content length: {avg_content_length:.2f} characters")
                    
                    # Generate summary
                    summary = await summarize_with_llm(processed_articles, topic)
                    summaries.append({
                        "topic": topic,
                        "summary": summary
                    })
        
        if not summaries:
            raise HTTPException(
                status_code=404,
                detail="Could not generate summaries for any topics"
            )
            
        return {"summaries": summaries}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error generating news summaries: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating news summaries: {str(e)}"
        )

@router.put("/users/{mobile_number}/topics")
async def update_user_topics(
    mobile_number: str,
    request: UpdateTopicsRequest
):
    """Update topics of interest for a user"""
    try:
        supabase = get_supabase_client()
        
        # Check if user exists
        existing_user = await supabase.get_user(mobile_number)
        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail=f"User with mobile number {mobile_number} not found"
            )
        
        # Update topics
        updated_user = await supabase.update_user_topics(
            mobile_number=mobile_number,
            topics=request.topics_of_interest
        )
        
        return {
            "message": "Topics updated successfully",
            "mobile_number": mobile_number,
            "updated_topics": updated_user['topics_of_interest']
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating topics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating topics: {str(e)}"
        ) 