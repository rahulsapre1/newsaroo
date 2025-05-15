#!/usr/bin/env python3
import asyncio
import logging
from src.news.search import search_news
from src.news.content import process_news_results
from src.news.summary import summarize_with_llm
from src.config import SERPAPI_KEY, OPENAI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_content():
    """Test the enhanced content fetching functionality"""
    topic = "technology"
    
    # Step 1: Search for news with enhanced content
    logger.info(f"Searching for news on topic: {topic}")
    news_results = await search_news(topic)
    
    if not news_results:
        logger.error("No news results found")
        return
    
    logger.info(f"Found {len(news_results)} news results")
    
    # Check if any articles have full_content
    articles_with_content = [article for article in news_results if "full_content" in article]
    logger.info(f"Articles with full content: {len(articles_with_content)} out of {len(news_results)}")
    
    # Step 2: Process the news results
    processed_articles = await process_news_results(news_results, max_articles=3)
    
    if not processed_articles:
        logger.error("No processed articles")
        return
    
    logger.info(f"Processed {len(processed_articles)} articles")
    
    # Print content length for each article
    for i, article in enumerate(processed_articles):
        content_length = len(article["content"])
        logger.info(f"Article {i+1}: '{article['title']}' - Content length: {content_length} chars")
        # Print first 100 chars of content
        logger.info(f"Content preview: {article['content'][:100]}...")
    
    # Step 3: Generate summary
    summary = await summarize_with_llm(processed_articles, topic)
    
    logger.info(f"Summary length: {len(summary)}")
    logger.info(f"Summary: {summary}")

if __name__ == "__main__":
    if not SERPAPI_KEY or not OPENAI_API_KEY:
        logger.error("API keys missing. Check your .env file.")
    else:
        asyncio.run(test_enhanced_content()) 