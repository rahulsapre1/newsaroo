"""
Content fetching module for the Newsaroo application.
Handles fetching and processing article content.
"""

import logging
import asyncio
import httpx
from ..config import DEFAULT_CONFIG

# Set up logging
logger = logging.getLogger(__name__)

async def fetch_article_content(url: str) -> str:
    """Fetch the content of a news article from its URL asynchronously
    
    Args:
        url (str): URL of the news article
        
    Returns:
        str: The HTML content of the article or snippet if content can't be fetched
    """
    try:
        # More sophisticated user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1"
        }
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.warning(f"Could not fetch full content from {url}: {str(e)}")
        # Instead of returning empty string, return the URL and note about access restriction
        return f"Article URL: {url}\nNote: Full content could not be accessed due to website restrictions. Please visit the URL directly."

async def process_news_results(news_results, max_articles=None):
    """Process the news results and fetch article content asynchronously
    
    Args:
        news_results (list): List of news results from SerpAPI
        max_articles (int, optional): Maximum number of articles to process.
            
    Returns:
        list: List of processed articles with content
    """
    max_articles = max_articles or DEFAULT_CONFIG["max_articles"]
    processed_articles = []
    
    if not news_results:
        logger.warning("No news results to process.")
        return processed_articles
    
    articles_to_process = news_results[:max_articles]
    logger.info(f"Fetching content for {len(articles_to_process)} articles...")
    print(f"Fetching content for {len(articles_to_process)} articles...")
    
    for article in articles_to_process:
        article_info = {
            "title": article.get("title", "Untitled"),
            "link": article.get("link", ""),
            "source": article.get("source", ""),
            "snippet": article.get("snippet", ""),
            "date": article.get("date", "")
        }
        
        if article_info["link"]:
            # If we can't get the content, we'll still have the snippet
            content = await fetch_article_content(article_info["link"])
            article_info["content"] = content if content else article_info["snippet"]
        else:
            article_info["content"] = article_info["snippet"]
        
        processed_articles.append(article_info)
    
    return processed_articles 