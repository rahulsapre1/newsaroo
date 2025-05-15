#!/usr/bin/env python3
import asyncio
import logging
import json
import sys
from src.api.routes import get_user_news_summaries
from fastapi import Path
from fastapi.testclient import TestClient
from src.main import app

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create test client
client = TestClient(app)

def test_api_endpoint():
    """Test the endpoint directly using FastAPI TestClient"""
    # Mobile number from the image
    mobile = "9876543210"
    
    # Make the API call
    response = client.get(f"/api/v1/users/{mobile}/summaries")
    
    # Print response status
    print(f"Status code: {response.status_code}")
    
    # Process response
    if response.status_code == 200:
        data = response.json()
        print(f"Number of summaries: {len(data.get('summaries', []))}")
        
        # Print each topic
        for i, summary in enumerate(data.get('summaries', [])):
            print(f"\nTopic {i+1}: {summary.get('topic')}")
            # Print first 100 chars of summary
            print(f"Summary preview: {summary.get('summary', '')[:100]}...")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_api_endpoint() 