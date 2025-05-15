"""
News search module for the Newsaroo application.
Handles searching for news articles using SerpAPI.
"""

import logging
from serpapi.google_search import GoogleSearch
from ..config import SERPAPI_KEY, DEFAULT_CONFIG
import asyncio
import httpx
import re
from bs4 import BeautifulSoup

# Set up logging
logger = logging.getLogger(__name__)

async def fetch_article_content(url, timeout=10):
    """Fetch article content from URL
    
    Args:
        url (str): URL of the article
        timeout (int): Timeout in seconds
        
    Returns:
        str: Article content or None if failed
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout, follow_redirects=True)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                
                # Get text and clean it
                text = soup.get_text(separator=' ', strip=True)
                
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Truncate if too long
                if len(text) > 3000:
                    text = text[:3000] + "..."
                
                return text
            else:
                logger.warning(f"Failed to fetch article content: {response.status_code}")
                return None
    except Exception as e:
        logger.warning(f"Error fetching article content: {str(e)}")
        return None

async def search_news(topic, api_key=None, time_period=None):
    """Search for news on the given topic using SerpAPI
    
    Args:
        topic (str): The news topic to search for
        api_key (str, optional): SerpAPI key. Defaults to the one in config.
        time_period (str, optional): Time period for news. Defaults to "1d" for 1 day.
        
    Returns:
        list: List of news results
    """
    # Use default API key if none provided
    api_key = api_key or SERPAPI_KEY
    
    # Use default time period if none provided
    time_period = time_period or DEFAULT_CONFIG["time_period"]
    
    if not api_key:
        logger.error("No SerpAPI key provided. Cannot search for news.")
        return []
    
    if not topic:
        logger.error("No topic provided for news search.")
        return []
    
    logger.info(f"Searching for news on '{topic}' from the last {time_period}...")
    
    # Configure the search parameters
    params = {
        "engine": "google_news",
        "q": topic,
        "time": time_period,
        "num": DEFAULT_CONFIG["max_articles"],
        "api_key": api_key,
        "gl": "us",  # Set to US results for better snippets
        "hl": "en",   # Set language to English
        "tbm": "nws",  # Search news tab specifically
        "tbs": f"qdr:{time_period}",  # Time period
    }
    
    try:
        # Execute the search in a non-blocking way
        search = GoogleSearch(params)
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, search.get_dict)
        
        # Check if we have news results
        if "news_results" in results and results["news_results"]:
            num_results = len(results["news_results"])
            logger.info(f"Found {num_results} news articles")
            
            # Log first result to debug structure
            if results["news_results"]:
                logger.info(f"Sample result structure: {results['news_results'][0]}")
                
            # Enhance results with full content for top articles (limit to 5 to avoid rate limiting)
            enhanced_results = []
            for article in results["news_results"][:5]:
                if "link" in article:
                    # Try to fetch full content
                    content = await fetch_article_content(article["link"])
                    if content:
                        article["full_content"] = content
                enhanced_results.append(article)
                
            # Add remaining articles without fetching content
            enhanced_results.extend(results["news_results"][5:])
            
            return enhanced_results
        else:
            logger.warning(f"No news results found for topic: {topic}")
            return []
    except Exception as e:
        logger.error(f"Error searching for news: {str(e)}")
        raise Exception(f"Failed to search news: {str(e)}")  # Propagate error for proper HTTP status 