"""
Main module for the Newsaroo application.
Entry point for the application.
"""

import logging
import argparse
import sys

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

def news_summarizer(topic=None):
    """Complete news summarizer function that runs the entire process
    
    Args:
        topic (str, optional): The news topic. If None, will prompt the user.
    
    Returns:
        str: The summarized news
    """
    # 1. Check API keys
    if not SERPAPI_KEY:
        logger.error("SERP API key not found. Please check your .env file.")
        return "Error: SERP API key not found. Please check your .env file."
    
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found. Please check your .env file.")
        return "Error: OpenAI API key not found. Please check your .env file."
    
    # 2. Get the topic if not provided
    if topic is None:
        topic = get_user_topic()
    
    logger.info(f"Starting news summarization for topic: {topic}")
    print(f"Searching for news on: {topic}")
    
    # 3. Search for news
    news_results = search_news(topic, SERPAPI_KEY)
    
    if not news_results:
        logger.warning(f"No news found for topic: {topic}")
        return "No news found for the given topic. Please try a different topic."
    
    # 4. Process the news results and fetch content
    processed_articles = process_news_results(news_results)
    
    if not processed_articles:
        logger.warning(f"No articles processed for topic: {topic}")
        return "No articles could be processed. Please try a different topic."
    
    # 5. Summarize the articles
    summary = summarize_with_llm(processed_articles, topic)
    
    # 6. Display the summary
    display_summary(summary, topic)
    
    logger.info(f"Completed news summarization for topic: {topic}")
    return summary

def main():
    """Main function to run the application"""
    parser = argparse.ArgumentParser(description='Newsaroo - A daily news summarizer')
    parser.add_argument('--topic', type=str, help='The news topic to search for')
    args = parser.parse_args()
    
    try:
        news_summarizer(args.topic)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        print("\nApplication terminated by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 