"""Structured logging configuration."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

import structlog


def configure_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
        json_format: Use JSON format for machine parsing
    """
    # Set up standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )
    
    # Common processors
    common_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Choose renderer based on format
    if json_format:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(
            colors=sys.stdout.isatty()
        )
    
    processors = common_processors + [renderer]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Set up file logging if requested
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Use JSON format for file logging
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        
        # Add to root logger
        logging.getLogger().addHandler(file_handler)


def get_logger(name: Optional[str] = None, **context) -> structlog.BoundLogger:
    """
    Get a logger instance with optional context.
    
    Args:
        name: Logger name (usually module name)
        **context: Additional context to bind
    
    Returns:
        Bound logger instance
    """
    logger = structlog.get_logger(name)
    
    if context:
        logger = logger.bind(**context)
    
    return logger


class LogContext:
    """Context manager for scoped logging context."""
    
    def __init__(self, **context):
        self.context = context
        self._token = None
    
    def __enter__(self):
        self._token = structlog.contextvars.bind_contextvars(**self.context)
        return self
    
    def __exit__(self, *args):
        if self._token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_agent_action(
    agent: str,
    action: str,
    duration_ms: int,
    success: bool,
    **extra
) -> None:
    """Log an agent action with standard fields."""
    logger = get_logger("agent_action")
    
    log_data = {
        "agent": agent,
        "action": action,
        "duration_ms": duration_ms,
        "success": success,
        **extra
    }
    
    if success:
        logger.info("agent_action", **log_data)
    else:
        logger.warning("agent_action_failed", **log_data)


def log_quality_check(
    section: str,
    iteration: int,
    score: int,
    gates_passed: bool,
    **extra
) -> None:
    """Log a quality check result."""
    logger = get_logger("quality")
    
    logger.info(
        "quality_check",
        section=section,
        iteration=iteration,
        score=score,
        gates_passed=gates_passed,
        **extra
    )
