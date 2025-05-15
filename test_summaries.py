#!/usr/bin/env python3
import logging
import asyncio
from src.news.search import search_news
from src.news.content import process_news_results
from src.news.summary import summarize_with_llm
from src.config import SERPAPI_KEY, OPENAI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_topic_summary(topic):
    try:
        logger.info(f"Testing summarization for topic: {topic}")
        
        # Search for news
        logger.info(f"Searching for news on topic: {topic}")
        news_results = await search_news(topic)
        
        if not news_results:
            logger.warning(f"No news results found for topic: {topic}")
            return None
        
        logger.info(f"Found {len(news_results)} news results for topic: {topic}")
        
        # Process articles
        processed_articles = await process_news_results(news_results)
        
        if not processed_articles:
            logger.warning(f"No processed articles for topic: {topic}")
            return None
        
        logger.info(f"Processed {len(processed_articles)} articles for topic: {topic}")
        
        # Generate summary
        summary = await summarize_with_llm(processed_articles, topic)
        
        logger.info(f"Summary for topic '{topic}': {summary[:100]}...")
        
        return {
            "topic": topic,
            "summary": summary
        }
    
    except Exception as e:
        logger.error(f"Error summarizing topic '{topic}': {str(e)}")
        return None

async def main():
    # Test topics
    topics = ["technology", "AI", "space"]
    
    # Process each topic
    results = []
    for topic in topics:
        result = await test_topic_summary(topic)
        if result:
            results.append(result)
    
    # Print results
    print(f"\nSummaries generated: {len(results)} out of {len(topics)} topics")
    for result in results:
        print(f"\n--- {result['topic']} ---")
        print(f"{result['summary'][:150]}...")

if __name__ == "__main__":
    if not SERPAPI_KEY or not OPENAI_API_KEY:
        logger.error("API keys missing. Check your .env file.")
    else:
        asyncio.run(main()) 