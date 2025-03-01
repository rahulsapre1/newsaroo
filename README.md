# Newsaroo

A daily news summarizer application that searches for news on a given topic, fetches the content, and summarizes it using an LLM.

## Features

- Search for news on a given topic over the last 24 hours
- Fetch and process article content
- Summarize the news using an LLM
- Display the "Top 3 important items I should know and why"

## Requirements

- Python 3.11+
- SerpAPI key
- OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/newsaroo.git
   cd newsaroo
   ```

2. Create a virtual environment:
   ```
   python -m venv .news_env
   source .news_env/bin/activate  # On Windows: .news_env\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERP_API_KEY=your_serpapi_key
   ```

## Usage

### Command Line

Run the application from the command line:

```
python -m src.main
```

You will be prompted to enter a news topic. Alternatively, you can specify the topic as a command-line argument:

```
python -m src.main --topic "artificial intelligence"
```

### As a Module

You can also use the application as a module in your own code:

```python
from src.main import news_summarizer

# Get a summary for a specific topic
summary = news_summarizer("artificial intelligence")

# Or let the application prompt the user for a topic
summary = news_summarizer()
```

## Project Structure

```
newsaroo/
├── .env                  # API keys (not tracked by git)
├── README.md            # Project documentation
├── requirements.txt     # Dependencies
├── src/
│   ├── __init__.py      # Makes src a Python package
│   ├── main.py          # Entry point for the application
│   ├── config.py        # Configuration and environment variables
│   ├── news/
│   │   ├── __init__.py  # Makes news a Python package
│   │   ├── search.py    # News search functionality
│   │   ├── content.py   # Content fetching and processing
│   │   └── summary.py   # Summarization using LLM
│   └── utils/
│       ├── __init__.py  # Makes utils a Python package
│       └── display.py   # Display utilities
└── tests/               # Unit tests
    └── __init__.py
```

## License

MIT

## Acknowledgements

- [SerpAPI](https://serpapi.com/) for providing the news search functionality
- [LiteLLM](https://github.com/BerriAI/litellm) for the LLM integration 