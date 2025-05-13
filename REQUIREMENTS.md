# Newsaroo Requirements

## System Requirements

### Package Manager
- **Homebrew** (for macOS)
  ```bash
  # Install Homebrew
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  
  # Add Homebrew to PATH
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
  eval "$(/opt/homebrew/bin/brew shellenv)"
  ```

### System Packages
- **ngrok** (for exposing local API)
  ```bash
  # Install using Homebrew
  brew install ngrok
  
  # Configure ngrok (required after installation)
  ngrok config add-authtoken YOUR_AUTH_TOKEN  # Replace with your token from ngrok.com
  ```

## Python Requirements
Python packages are managed in `requirements.txt`. Install them using:
```bash
# Create and activate virtual environment
python3 -m venv .newsaroo_env
source .newsaroo_env/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file with the following:
```
SERPAPI_KEY=your_serp_api_key
OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

### API Server
```bash
# Start the API server
python run.py  # Runs on port 8080

# Expose API using ngrok
ngrok http 8080
```

### CLI Mode
```bash
python -m src.cli --topic "your topic"
``` 