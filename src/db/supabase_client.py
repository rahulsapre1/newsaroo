"""
Supabase client configuration for the Newsaroo application.
"""

from supabase import create_client
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_API_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")

def get_supabase_client():
    """Create and return Supabase client"""
    # Add debug logging
    logger.info(f"Creating Supabase client with URL: {SUPABASE_URL}")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL or key is missing")
        
    return create_client(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    ) 