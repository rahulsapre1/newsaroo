"""
Content fetching module for the Newsaroo application.
Handles fetching and processing article content.
"""

import logging
import time
import requests
from ..config import DEFAULT_CONFIG

# Set up logging
logger = logging.getLogger(__name__)

def fetch_article_content(url):
    """Fetch the content of a news article from its URL
    
    Args:
        url (str): URL of the news article
        
    Returns:
        str: The HTML content of the article
    """
    try:
        # Set a user agent to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except Exception as e:
        logger.error(f"Error fetching article from {url}: {e}")
        print(f"Error fetching article from {url}: {e}")
        return ""

def process_news_results(news_results, max_articles=None):
    """Process the news results and fetch article content
    
    Args:
        news_results (list): List of news results from SerpAPI
        max_articles (int, optional): Maximum number of articles to process.
            Defaults to the value in DEFAULT_CONFIG.
        
    Returns:
        list: List of processed articles with content
    """
    # Use default max_articles if none provided
    max_articles = max_articles or DEFAULT_CONFIG["max_articles"]
    
    processed_articles = []
    
    if not news_results:
        logger.warning("No news results to process.")
        return processed_articles
    
    # Limit the number of articles to process
    articles_to_process = news_results[:max_articles]
    
    logger.info(f"Fetching content for {len(articles_to_process)} articles...")
    print(f"Fetching content for {len(articles_to_process)} articles...")
    
    for i, article in enumerate(articles_to_process):
        title = article.get("title", "Untitled")
        logger.info(f"Processing article {i+1}/{len(articles_to_process)}: {title}")
        print(f"Processing article {i+1}/{len(articles_to_process)}: {title}")
        
        # Extract article information
        article_info = {
            "title": title,
            "link": article.get("link", ""),
            "source": article.get("source", ""),
            "snippet": article.get("snippet", ""),
            "date": article.get("date", "")
        }
        
        # Fetch the article content if we have a link
        if article_info["link"]:
            article_info["content"] = fetch_article_content(article_info["link"])
        else:
            article_info["content"] = ""
        
        processed_articles.append(article_info)
        
        # Add a small delay to avoid overwhelming servers
        time.sleep(1)
    
    return processed_articles 