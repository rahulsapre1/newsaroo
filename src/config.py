"""
Configuration module for the Newsaroo application.
Handles loading environment variables and setting up configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
SERPAPI_KEY = os.environ.get("SERP_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check if keys are available
if not SERPAPI_KEY:
    print("Warning: SERP_API_KEY not found in environment variables. Please check your .env file.")

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables. Please check your .env file.")

# Set the OpenAI API key for litellm
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY if OPENAI_API_KEY else ""

# Default configuration
DEFAULT_CONFIG = {
    "max_articles": 10,  # Maximum number of articles to process
    "time_period": "1d",  # Default time period for news search (1 day)
    "llm_model": "gpt-4o",  # Default LLM model to use
    "max_tokens": 1000,  # Maximum tokens for LLM response
}

# LLM Configuration
LLM_CONFIG = {
    "model": DEFAULT_CONFIG["llm_model"],
    "max_tokens": DEFAULT_CONFIG["max_tokens"],
    "system_message": "You are a helpful news summarization assistant that provides concise, accurate summaries of recent news."
}

# Add Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_API_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

# Add some debug logging
print(f"Loaded SUPABASE_URL: {SUPABASE_URL}")  # Temporary debug line 