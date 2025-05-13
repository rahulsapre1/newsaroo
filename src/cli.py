"""
Command-line interface for the Newsaroo application.
"""

import argparse
import logging
import sys
import asyncio
from .news.search import search_news
from .news.content import process_news_results
from .news.summary import summarize_with_llm
from .utils.display import display_summary, get_user_topic
from .config import SERPAPI_KEY, OPENAI_API_KEY

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

async def news_summarizer(topic=None):
    """Complete news summarizer function that runs the entire process"""
    if not SERPAPI_KEY or not OPENAI_API_KEY:
        logger.error("API keys not found. Please check your .env file.")
        return "Error: API keys not found. Please check your .env file."
    
    if topic is None:
        topic = get_user_topic()
    
    logger.info(f"Starting news summarization for topic: {topic}")
    print(f"Searching for news on: {topic}")
    
    news_results = await search_news(topic, SERPAPI_KEY)
    if not news_results:
        return "No news found for the given topic. Please try a different topic."
    
    processed_articles = await process_news_results(news_results)
    if not processed_articles:
        return "No articles could be processed. Please try a different topic."
    
    summary = await summarize_with_llm(processed_articles, topic)
    display_summary(summary, topic)
    
    return summary

def main():
    """Entry point for CLI"""
    parser = argparse.ArgumentParser(description='Newsaroo - A daily news summarizer')
    parser.add_argument('--topic', type=str, help='The news topic to search for')
    args = parser.parse_args()
    
    try:
        asyncio.run(news_summarizer(args.topic))
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 