import uvicorn
import os

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    ) 