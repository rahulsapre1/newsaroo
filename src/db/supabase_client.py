"""
Supabase client configuration for the Newsaroo application.
"""

import os
import logging
from typing import Optional, Dict, Any
from supabase import create_client, Client
from ..config import SUPABASE_API_URL, SUPABASE_API_KEY

# Set up logging
logger = logging.getLogger(__name__)

class SupabaseManager:
    _instance: Optional['SupabaseManager'] = None
    _client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._client:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize the Supabase client with service role"""
        if not SUPABASE_API_URL or not SUPABASE_API_KEY:
            error_msg = "Supabase configuration missing. Check SUPABASE_API_URL and SUPABASE_API_KEY in .env"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # Initialize with service role key
            self._client = create_client(SUPABASE_API_URL, SUPABASE_API_KEY)
            logger.info("Supabase client created successfully with service role")
        except Exception as e:
            error_msg = f"Failed to create Supabase client: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    @property
    def client(self) -> Client:
        """Get the Supabase client instance"""
        if not self._client:
            self._initialize_client()
        return self._client

    async def insert_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new user into the newsroom_users table
        
        Args:
            user_data: Dictionary containing user data
            
        Returns:
            Dict containing the inserted user data
            
        Raises:
            Exception: If insertion fails
        """
        try:
            result = self.client.table('newsroom_users').insert(user_data).execute()
            if not result.data:
                raise Exception("No data returned from insert operation")
            logger.info(f"Successfully inserted user: {user_data.get('mobile_number')}")
            return result.data[0]
        except Exception as e:
            error_msg = f"Failed to insert user: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def get_user(self, mobile_number: str) -> Optional[Dict[str, Any]]:
        """Get user data by mobile number
        
        Args:
            mobile_number: User's mobile number
            
        Returns:
            Dict containing user data or None if not found
        """
        try:
            result = self.client.table('newsroom_users')\
                .select("*")\
                .eq('mobile_number', mobile_number)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Failed to get user: {str(e)}")
            return None

    async def update_user_topics(self, mobile_number: str, topics: list) -> Dict[str, Any]:
        """Update user's topics of interest
        
        Args:
            mobile_number: User's mobile number
            topics: List of topics
            
        Returns:
            Dict containing updated user data
            
        Raises:
            Exception: If update fails
        """
        try:
            result = self.client.table('newsroom_users')\
                .update({'topics_of_interest': topics})\
                .eq('mobile_number', mobile_number)\
                .execute()
            if not result.data:
                raise Exception("No data returned from update operation")
            return result.data[0]
        except Exception as e:
            error_msg = f"Failed to update user topics: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

def get_supabase_client() -> SupabaseManager:
    """Get the Supabase manager instance with service role"""
    return SupabaseManager() 