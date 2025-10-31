"""
Logging utilities for the AI Research Assistant.
"""
import logging
import sys
from pathlib import Path
from app.config import LOG_LEVEL, LOG_FILE


def setup_logger(name: str = "ai_assistant", level: str = None) -> logging.Logger:
    """
    Set up and configure logger.
    
    Args:
        name: Logger name
        level: Logging level (default from config)
    
    Returns:
        Configured logger instance
    """
    level = level or LOG_LEVEL
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    if LOG_FILE:
        log_path = Path(LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


# Default logger instance
logger = setup_logger()
