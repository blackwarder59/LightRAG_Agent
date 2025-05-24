"""
Logging Configuration Utility

This module sets up structured logging for the LightRAG Agent application
using loguru for enhanced logging capabilities.
"""

import sys
from pathlib import Path
from loguru import logger

from app.config.settings import settings


def setup_logging():
    """
    Configure loguru logger with appropriate settings for the application.
    
    This function:
    - Removes default loguru handler
    - Sets up console logging with colors and formatting
    - Sets up file logging if configured
    - Configures log levels and filtering
    """
    # Remove default loguru handler
    logger.remove()
    
    # Console logging configuration
    logger.add(
        sys.stdout,
        format=settings.LOG_FORMAT,
        level=settings.LOG_LEVEL.upper(),
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File logging configuration (if specified)
    if settings.LOG_FILE:
        log_file_path = Path(settings.LOG_FILE)
        
        # Ensure log directory exists
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add file handler with rotation
        logger.add(
            str(log_file_path),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.LOG_LEVEL.upper(),
            rotation="10 MB",  # Rotate when file reaches 10MB
            retention="30 days",  # Keep logs for 30 days
            compression="zip",  # Compress rotated logs
            backtrace=True,
            diagnose=True
        )
    
    # Log startup message
    logger.info(f"Logging initialized - Level: {settings.LOG_LEVEL}")
    if settings.LOG_FILE:
        logger.info(f"Log file: {settings.LOG_FILE}")


def get_logger(name: str):
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logger.bind(name=name) 