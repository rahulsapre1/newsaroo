"""
Configuration module for the Newsaroo application.
Handles loading environment variables and setting up configuration.
"""

import os
from dotenv import load_dotenv
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# API Keys
SERPAPI_KEY = os.environ.get("SERP_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SUPABASE_API_URL = os.environ.get("SUPABASE_API_URL")
SUPABASE_API_KEY = os.environ.get("SUPABASE_API_KEY")

# Check if keys are available
if not SERPAPI_KEY:
    logger.warning("SERP_API_KEY not found in environment variables. Please check your .env file.")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables. Please check your .env file.")

if not SUPABASE_API_URL or not SUPABASE_API_KEY:
    logger.warning("Supabase configuration not found. Please check SUPABASE_API_URL and SUPABASE_API_KEY in your .env file.")

# Set the OpenAI API key for litellm
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY if OPENAI_API_KEY else ""

# Default configuration
DEFAULT_CONFIG = {
    "max_articles": 10,  # Maximum number of articles to process
    "time_period": "1d",  # Default time period for news search (1 day)
    "llm_model": "gpt-4",  # Default LLM model to use
    "max_tokens": 1000,  # Maximum tokens for LLM response
}

# LLM Configuration
LLM_CONFIG = {
    "model": DEFAULT_CONFIG["llm_model"],
    "max_tokens": DEFAULT_CONFIG["max_tokens"],
    "system_message": "You are a helpful news summarization assistant that provides concise, accurate summaries of recent news."
}

# Log configuration status
logger.info("Configuration loaded - API Keys status:")
logger.info(f"SERP API Key: {'Present' if SERPAPI_KEY else 'Missing'}")
logger.info(f"OpenAI API Key: {'Present' if OPENAI_API_KEY else 'Missing'}")
logger.info(f"Supabase Configuration: {'Present' if (SUPABASE_API_URL and SUPABASE_API_KEY) else 'Missing'}") 