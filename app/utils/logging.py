import logging
import sys
from typing import Optional
from app.core.config import settings


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up application logging."""
    
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Get logger for the application
    logger = logging.getLogger("vyralflow")
    
    # Set debug level if in debug mode
    if settings.debug:
        logger.setLevel(logging.DEBUG)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f"vyralflow.{name}")


# Create default logger
logger = setup_logging()