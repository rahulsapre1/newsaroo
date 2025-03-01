"""
Display utilities for the Newsaroo application.
Handles displaying the news summary.
"""

import logging

# Set up logging
logger = logging.getLogger(__name__)

def display_summary(summary, topic):
    """Display the final news summary
    
    Args:
        summary (str): The summarized news
        topic (str): The original search topic
    """
    separator = "=" * 80
    
    print("\n" + separator)
    print(f"NEWS SUMMARY FOR: {topic.upper()}")
    print(separator)
    print(summary)
    print(separator)
    
    logger.info(f"Displayed summary for topic: {topic}")

def get_user_topic():
    """Get the news topic from the user via terminal input
    
    Returns:
        str: The news topic
    """
    topic = input("Enter the news topic you're interested in: ")
    logger.info(f"User entered topic: {topic}")
    return topic 