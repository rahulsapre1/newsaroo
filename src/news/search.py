"""
News search module for the Newsaroo application.
Handles searching for news articles using SerpAPI.
"""

import logging
from serpapi import GoogleSearch
from ..config import SERPAPI_KEY, DEFAULT_CONFIG

# Set up logging
logger = logging.getLogger(__name__)

def search_news(topic, api_key=None, time_period=None):
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
    
    logger.info(f"Searching for news on '{topic}' from the last 24 hours...")
    print(f"Searching for news on '{topic}' from the last 24 hours...")
    
    # Configure the search parameters
    params = {
        "engine": "google",
        "q": f"{topic} news",
        "tbm": "nws",  # News search
        "tbs": f"qdr:{time_period}",  # Time period (1d = 1 day)
        "num": DEFAULT_CONFIG["max_articles"],  # Number of results
        "api_key": api_key
    }
    
    try:
        # Execute the search
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check if we have news results
        if "news_results" in results and results["news_results"]:
            num_results = len(results["news_results"])
            logger.info(f"Found {num_results} news articles")
            print(f"Found {num_results} news articles")
            return results["news_results"]
        else:
            logger.warning("No news results found.")
            print("No news results found. Try a different topic or time period.")
            return []
    except Exception as e:
        logger.error(f"Error searching for news: {e}")
        print(f"Error searching for news: {e}")
        return [] 