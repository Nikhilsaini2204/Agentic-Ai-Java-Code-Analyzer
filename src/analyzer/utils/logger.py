"""
Professional logging setup with structured JSON logs and beautiful console output.
"""

import sys

from loguru import logger

from config.settings import settings


def setup_logger() -> None:
    """Configure application logger with appropriate handlers."""

    # Remove default handler
    logger.remove()

    # Console handler with colors (development)
    if settings.is_development:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level,
            colorize=True,
        )
    else:
        # Simple format for production
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.log_level,
        )

    # File handler with rotation
    log_file = settings.log_dir / "agent_{time:YYYY-MM-DD}.log"
    logger.add(
        log_file,
        rotation="00:00",  # Rotate at midnight
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",  # Always log debug to file
        enqueue=True,  # Async logging
    )

    # JSON logs for production (machine-readable)
    if settings.is_production:
        json_log_file = settings.log_dir / "agent_{time:YYYY-MM-DD}.json"
        logger.add(
            json_log_file,
            rotation="00:00",
            retention="90 days",
            compression="zip",
            serialize=True,  # JSON format
            level="INFO",
            enqueue=True,
        )

    logger.info(f"Logger initialized - Environment: {settings.environment}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Logs directory: {settings.log_dir}")


def get_logger(name: str):
    """Get a logger instance for a module."""
    return logger.bind(module=name)
