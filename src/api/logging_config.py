import logging
import sys
from datetime import datetime

def setup_logging():
    """Sets up logging configuration for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("ml_inference_system")

logger = setup_logging()