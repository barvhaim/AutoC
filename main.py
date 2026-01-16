"""Main entry point for AutoC API server."""

import logging

from dotenv import load_dotenv

from api.server import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
