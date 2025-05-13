"""
Main module for the Newsaroo API application.
"""

import logging
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
from .api.models import NewsRequest, NewsResponse, Article
from .news.search import search_news
from .news.content import process_news_results
from .news.summary import summarize_with_llm
from .config import SERPAPI_KEY, OPENAI_API_KEY
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("newsaroo.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Newsaroo API",
    description="News summarization API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our router
app.include_router(router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {"status": "healthy"}

async def process_news_request(topic: str, time_period: str, max_articles: int) -> NewsResponse:
    """Common processing logic for both GET and POST requests"""
    try:
        # Check API keys
        if not SERPAPI_KEY:
            raise HTTPException(status_code=500, detail="SERP API key not configured")
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Search for news
        news_results = await search_news(
            topic=topic,
            api_key=SERPAPI_KEY,
            time_period=time_period
        )
        
        if not news_results:
            raise HTTPException(
                status_code=404,
                detail=f"No news found for topic: {topic}"
            )

        # Process articles
        processed_articles = await process_news_results(
            news_results=news_results,
            max_articles=max_articles
        )

        if not processed_articles:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to process articles for topic: {topic}"
            )

        # Generate summary
        try:
            summary = await summarize_with_llm(processed_articles, topic)
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate summary: {str(e)}"
            )

        # Create response
        articles = [
            Article(
                title=article.get("title", "Untitled"),
                source_name=article["source"]["name"] if isinstance(article["source"], dict) else str(article.get("source", "Unknown Source")),
                source_details=article["source"] if isinstance(article["source"], dict) else {},
                summary=article.get("snippet") or article.get("description") or "No preview available"
            )
            for article in processed_articles
        ]

        return NewsResponse(
            topic=topic,
            summary=summary,
            articles=articles,
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/summarize", response_model=NewsResponse)
async def summarize_news_get(
    topic: str = Query(..., description="The news topic to search for"),
    time_period: str = Query("1d", description="Time period for news (e.g., 1d, 7d)"),
    max_articles: int = Query(5, description="Maximum number of articles to process", ge=1, le=20)
):
    """Get a summary of news articles for a specific topic using GET method"""
    return await process_news_request(topic, time_period, max_articles)

@app.post("/summarize", response_model=NewsResponse)
async def summarize_news_post(request: NewsRequest):
    """Get a summary of news articles for a specific topic using POST method"""
    return await process_news_request(
        topic=request.topic,
        time_period=request.time_period,
        max_articles=request.max_articles
    ) 