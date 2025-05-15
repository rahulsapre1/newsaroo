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
        
        # Extract content - prioritize full_content if available
        content = None
        if "full_content" in article:
            content = article["full_content"]
            logger.info(f"Using full content for article: {article.get('title', 'Untitled')}")
        else:
            # Extract snippet - SERP API returns it as 'snippet' or 'description'
            content = article.get("snippet") or article.get("description")
        
        # If we still don't have content, use a placeholder
        if not content:
            content = "No content available"
            
        # Create a summary snippet (shorter version of content)
        snippet = content[:200] + "..." if len(content) > 200 else content
        
        article_info = {
            "title": article.get("title", "Untitled"),
            "source": article.get("source", "Unknown Source"),
            "content": content,
            "snippet": snippet
        }
        processed_articles.append(article_info)
        
        # Log processed article (truncate content for logging)
        log_info = article_info.copy()
        if len(log_info["content"]) > 100:
            log_info["content"] = log_info["content"][:100] + "..."
        logger.info(f"Processed article: {log_info}")
    
    return processed_articles 