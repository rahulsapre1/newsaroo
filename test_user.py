#!/usr/bin/env python3
import logging
import asyncio
from src.db.supabase_client import get_supabase_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_user_data():
    try:
        # Get Supabase client
        client = get_supabase_client()
        
        # Fetch user data
        mobile = "9876543210"
        user = await client.get_user(mobile)
        
        print(f"User data: {user}")
        
        if user:
            topics = user.get('topics_of_interest', [])
            print(f"Topics of interest: {topics}")
            print(f"Number of topics: {len(topics)}")
            print(f"Topics type: {type(topics)}")
            
            # Print each topic individually
            for i, topic in enumerate(topics):
                print(f"Topic {i+1}: {topic}")
        else:
            print(f"No user found with mobile number: {mobile}")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_user_data()) 