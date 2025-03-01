"""
Summary module for the Newsaroo application.
Handles summarizing news articles using LLM.
"""

import logging
import litellm
from ..config import OPENAI_API_KEY, LLM_CONFIG

# Set up logging
logger = logging.getLogger(__name__)

def summarize_with_llm(articles, topic, model=None, max_tokens=None):
    """Summarize the news articles using an LLM
    
    Args:
        articles (list): List of processed articles
        topic (str): The original search topic
        model (str, optional): LLM model to use. Defaults to the one in LLM_CONFIG.
        max_tokens (int, optional): Maximum tokens for LLM response. 
            Defaults to the value in LLM_CONFIG.
        
    Returns:
        str: Summarized news in the requested format
    """
    if not articles:
        logger.warning("No articles found to summarize.")
        return "No articles found to summarize."
    
    # Use default model and max_tokens if none provided
    model = model or LLM_CONFIG["model"]
    max_tokens = max_tokens or LLM_CONFIG["max_tokens"]
    
    if not OPENAI_API_KEY:
        logger.error("No OpenAI API key provided. Cannot summarize articles.")
        return "Error: No OpenAI API key provided. Please check your .env file."
    
    logger.info("Summarizing news articles using LLM...")
    print("Summarizing news articles using LLM...")
    
    # Prepare the context for the LLM
    context = f"I need a summary of recent news about '{topic}'. Here are the articles I found:\n\n"
    
    for i, article in enumerate(articles):
        context += f"Article {i+1}: {article['title']}\n"
        context += f"Source: {article['source']}\n"
        context += f"Date: {article['date']}\n"
        context += f"Snippet: {article['snippet']}\n\n"
    
    # Create the prompt for the LLM
    prompt = f"""{context}
    
    Based on these articles, provide me with the "Top 3 important items I should know about {topic} and why they matter".
    
    Format your response as a numbered list with a brief explanation for each item.
    Focus on the most significant developments or insights from the last 24 hours.
    """
    
    try:
        # Configure litellm
        litellm.set_verbose = False
        
        # Call the LLM using litellm
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": LLM_CONFIG["system_message"]},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        
        # Extract the summary from the response
        summary = response.choices[0].message.content
        logger.info("Successfully generated summary")
        return summary
    except Exception as e:
        error_msg = f"Error summarizing with LLM: {e}"
        logger.error(error_msg)
        print(error_msg)
        return "Error generating summary. Please check your API keys and try again." 