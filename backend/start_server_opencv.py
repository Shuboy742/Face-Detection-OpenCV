#!/usr/bin/env python3
"""
Start the Voice-Based Greeting Agent API server with OpenCV face detection
"""

import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Voice-Based Greeting Agent API with OpenCV face detection...")
    
    uvicorn.run(
        "app.main_opencv:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )
