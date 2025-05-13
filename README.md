# Newsaroo

A powerful news summarization API that provides AI-powered summaries of current news topics.

## Features
- Search for news articles on any topic
- Customize time period (1-7 days) and number of articles
- AI-powered summarization
- Available as both API and CLI tool
- Support for exposing API via ngrok

## Requirements
See [REQUIREMENTS.md](REQUIREMENTS.md) for detailed installation instructions for:
- Homebrew (macOS package manager)
- ngrok (for exposing local API)
- Python dependencies
- Environment variables

## Quick Start

1. Install system requirements:
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ngrok
brew install ngrok
```

2. Set up Python environment:
```bash
# Create and activate virtual environment
python3 -m venv .newsaroo_env
source .newsaroo_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. Run the API:
```bash
python run.py
```

4. (Optional) Expose API using ngrok:
```bash
ngrok http 8080
```

## API Usage

### Get News Summary
```bash
curl -X POST http://localhost:8080/api/v1/news/summarize \
-H "Content-Type: application/json" \
-d '{
    "topic": "artificial intelligence",
    "time_period": "3d",
    "max_articles": 5
}'
```

## CLI Usage
```bash
python -m src.cli --topic "artificial intelligence"
```

## Documentation
- API documentation available at: `http://localhost:8080/docs`
- Alternative documentation at: `http://localhost:8080/redoc`

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