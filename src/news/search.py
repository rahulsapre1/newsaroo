"""
News search module for the Newsaroo application.
Handles searching for news articles using SerpAPI.
"""

import logging
from serpapi.google_search import GoogleSearch
from ..config import SERPAPI_KEY, DEFAULT_CONFIG
import asyncio
# Set up logging
logger = logging.getLogger(__name__)

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
        "hl": "en"   # Set language to English
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
            return results["news_results"]
        else:
            logger.warning(f"No news results found for topic: {topic}")
            return []
    except Exception as e:
        logger.error(f"Error searching for news: {str(e)}")
        raise Exception(f"Failed to search news: {str(e)}")  # Propagate error for proper HTTP status 