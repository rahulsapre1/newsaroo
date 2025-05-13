"""
Content processing module for the Newsaroo application.
Processes article snippets from SERP API.
"""

import logging
from ..config import DEFAULT_CONFIG

# Set up logging
logger = logging.getLogger(__name__)

async def process_news_results(news_results, max_articles=None):
    """Process the news results using snippets from SERP API
    
    Args:
        news_results (list): List of news results from SERP API
        max_articles (int, optional): Maximum number of articles to process.
            
    Returns:
        list: List of processed articles
    """
    max_articles = max_articles or DEFAULT_CONFIG["max_articles"]
    processed_articles = []
    
    if not news_results:
        logger.warning("No news results to process.")
        return processed_articles
    
    articles_to_process = news_results[:max_articles]
    logger.info(f"Processing {len(articles_to_process)} articles...")
    
    for article in articles_to_process:
        # Log raw article data to debug
        logger.info(f"Raw article data: {article}")
        
        # Extract snippet - SERP API returns it as 'snippet' or 'description'
        snippet = article.get("snippet") or article.get("description")
        
        article_info = {
            "title": article.get("title", "Untitled"),
            "source": article.get("source", "Unknown Source"),
            "content": snippet if snippet else "No content available",
            "snippet": snippet if snippet else "No preview available"
        }
        processed_articles.append(article_info)
        
        # Log processed article
        logger.info(f"Processed article: {article_info}")
    
    return processed_articles 