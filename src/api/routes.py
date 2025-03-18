"""
API routes for the Newsaroo application.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from src.api.models import NewsResponse, UserRegistration, UserResponse, UpdateTopicsRequest
from src.config import SERPAPI_KEY, OPENAI_API_KEY, DEFAULT_CONFIG
from src.news.search import search_news
from src.news.content import process_news_results
from src.news.summary import summarize_with_llm
from src.db.supabase_client import get_supabase_client
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/news_summary")
async def news_summarizer(
    topic: str = Query(..., description="The news topic to search for", min_length=2),
    max_articles: int = Query(
        default=DEFAULT_CONFIG["max_articles"], 
        description="Maximum number of articles to process",
        ge=1,  # greater than or equal to 1
        le=20  # less than or equal to 20
    ),
    time_period: str = Query(
        default=DEFAULT_CONFIG["time_period"],
        description="Time period for news search (e.g., 1d, 7d)",
        pattern="^[1-7]d$"  # only allow 1d to 7d
    )
):
    """Complete news summarizer endpoint that runs the entire process
    
    Args:
        topic (str): The news topic to search for
        max_articles (int, optional): Maximum number of articles to process. Defaults to 10.
        time_period (str, optional): Time period for news search. Defaults to "1d".
    
    Returns:
        dict: Contains topic, summary and articles
    """
    # 1. Check API keys
    if not SERPAPI_KEY:
        logger.error("SERP API key not found. Please check your .env file.")
        raise HTTPException(
            status_code=500,
            detail="Error: SERP API key not found. Please check your .env file."
        )
    
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found. Please check your .env file.")
        raise HTTPException(
            status_code=500,
            detail="Error: OpenAI API key not found. Please check your .env file."
        )
    
    logger.info(f"Starting news summarization for topic: {topic}")
    
    try:
        # 3. Search for news
        news_results = await search_news(topic, SERPAPI_KEY, time_period)
        
        if not news_results:
            logger.warning(f"No news found for topic: {topic}")
            raise HTTPException(
                status_code=404,
                detail="No news found for the given topic. Please try a different topic."
            )
        
        # 4. Process the news results and fetch content
        processed_articles = await process_news_results(news_results, max_articles)
        
        if not processed_articles:
            logger.warning(f"No articles processed for topic: {topic}")
            raise HTTPException(
                status_code=404,
                detail="No articles could be processed. Please try a different topic."
            )
        
        # 5. Summarize the articles
        summary = await summarize_with_llm(processed_articles, topic)
        
        logger.info(f"Completed news summarization for topic: {topic}")
        
        # Simplify the article information to just title and link
        simplified_articles = [
            {
                "title": article["title"],
                "link": article["link"]
            }
            for article in processed_articles
        ]
        
        # Return simplified response
        return {
            "topic": topic,
            "summary": summary,
            "articles": simplified_articles,
            "metadata": {
                "articles_found": len(simplified_articles),
                "time_period": time_period
            }
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"An error occurred: {e}")
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