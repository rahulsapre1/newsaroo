"""
Main module for the Newsaroo API application.
"""

import logging
import sys
from fastapi import FastAPI, HTTPException
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

@app.post("/summarize", response_model=NewsResponse)
async def summarize_news(request: NewsRequest):
    """Get a summary of news articles for a specific topic"""
    try:
        if not SERPAPI_KEY or not OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="API keys not configured"
            )

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

        processed_articles = await process_news_results(
            news_results=news_results,
            max_articles=request.max_articles
        )

        summary = await summarize_with_llm(processed_articles, request.topic)

        articles = [
            Article(
                title=article["title"],
                source=article["source"],
                summary=article["content"][:200] + "..."
            )
            for article in processed_articles
        ]

        return NewsResponse(
            topic=request.topic,
            summary=summary,
            articles=articles,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 