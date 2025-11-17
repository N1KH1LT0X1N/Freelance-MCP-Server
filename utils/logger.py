"""
Structured logging configuration for Freelance MCP Server

Provides JSON-formatted logs with context, request tracking, and multiple output handlers.
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import os


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        if hasattr(record, 'tool_name'):
            log_data['tool_name'] = record.tool_name

        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms

        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id

        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    log_file: str = "logs/freelance_mcp.log",
    json_format: bool = True,
    console_output: bool = True
) -> None:
    """
    Setup logging configuration

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        json_format: Use JSON format for logs
        console_output: Enable console output
    """
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Get log level from environment or parameter
    log_level = os.getenv('LOG_LEVEL', level).upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(numeric_level)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)

    # Set formatters
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if console_output:
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Log startup
    root_logger.info(f"Logging initialized at {log_level} level")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding contextual information to logs"""

    def __init__(self, logger: logging.Logger, **kwargs):
        """
        Initialize log context

        Args:
            logger: Logger instance
            **kwargs: Context fields to add to logs
        """
        self.logger = logger
        self.context = kwargs
        self.original_factory = logging.getLogRecordFactory()

    def __enter__(self):
        """Enter context - add fields to log records"""
        def record_factory(*args, **kwargs):
            record = self.original_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - restore original factory"""
        logging.setLogRecordFactory(self.original_factory)


# Example usage:
if __name__ == "__main__":
    # Setup logging
    setup_logging(level="DEBUG", json_format=True)

    logger = get_logger(__name__)

    # Basic logging
    logger.info("Server started")
    logger.debug("Debug information")
    logger.warning("Warning message")

    # Logging with context
    with LogContext(logger, request_id="req-123", tool_name="search_gigs"):
        logger.info("Tool called")
        logger.debug("Processing request")

    # Error logging
    try:
        raise ValueError("Example error")
    except Exception as e:
        logger.error("Error occurred", exc_info=True)
