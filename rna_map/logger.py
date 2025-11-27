"""Logging Setup Module

This module provides functions to set up logging configurations for Python applications.
It includes functionalities to set up root-level logging, application-level logging, and
to get logger instances with specific module names.

This module is designed to work well both as a standalone application and as a library
that can be imported by other packages. When used as a library, loggers will propagate
to parent loggers, allowing the parent application to control logging configuration.

Functions:
    - setup_logging(file_name: str = None, debug: bool = False) -> logging.Logger
        Set up the root logging configuration with optional file logging.
        Only adds handlers if none exist to avoid duplication.

    - setup_applevel_logger(
        logger_name: str = APP_LOGGER_NAME,
        is_debug: bool = False,
        file_name: str = None
    ) -> logging.Logger
        Set up and configure an application-level logger.
        Only adds handlers if none exist to avoid duplication.

    - get_logger(module_name: str = "") -> logging.Logger
        Get a logger instance with the specified module name.
        Works without requiring setup - loggers propagate to parent by default.

    - is_logging_configured() -> bool
        Check if logging has been configured (handlers exist).
"""

import logging
import sys
from typing import Optional

# logging #####################################################################

APP_LOGGER_NAME = "rna-map"

# Initialize with NullHandler to prevent "No handlers found" warnings
# when used as a library without explicit logging setup
_root_logger = logging.getLogger(APP_LOGGER_NAME)
if not _root_logger.handlers:
    _root_logger.addHandler(logging.NullHandler())


def _has_handler_of_type(logger: logging.Logger, handler_type: type) -> bool:
    """Check if logger has a handler of the specified type.

    Args:
        logger: The logger to check.
        handler_type: The handler class to look for.

    Returns:
        bool: True if a handler of the specified type exists.
    """
    return any(isinstance(h, handler_type) for h in logger.handlers)


def is_logging_configured() -> bool:
    """Check if logging has been configured.

    Returns:
        bool: True if any handlers exist on the root logger or app logger.
    """
    root_logger = logging.getLogger()
    app_logger = logging.getLogger(APP_LOGGER_NAME)
    return bool(root_logger.handlers) or bool(app_logger.handlers)


def setup_logging(
    file_name: Optional[str] = None, debug: bool = False
) -> logging.Logger:
    """Set up root logging configuration.

    This function configures the root logger. It checks for existing handlers
    to avoid duplication when used as a library. If the root logger already has
    handlers, it will only add a file handler if specified.

    Args:
        file_name: Optional log file path. If provided, logs will be written to file.
        debug: If True, set logging level to DEBUG, otherwise INFO.

    Returns:
        logging.Logger: The configured root logger.
    """
    root_logger = logging.getLogger()
    level = logging.DEBUG if debug else logging.INFO
    root_logger.setLevel(level)

    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")

    # Only add console handler if none exists
    if not _has_handler_of_type(root_logger, logging.StreamHandler):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Always add file handler if specified (user may want multiple file handlers)
    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def setup_applevel_logger(
    logger_name: str = APP_LOGGER_NAME,
    is_debug: bool = False,
    file_name: Optional[str] = None,
) -> logging.Logger:
    """Set up and configure an application-level logger.

    This function configures a named logger. It checks for existing handlers
    to avoid duplication when used as a library. The logger will propagate
    to parent loggers by default, allowing parent applications to control logging.

    Args:
        logger_name: The name of the logger. Defaults to APP_LOGGER_NAME.
        is_debug: If True, set logging level to DEBUG, otherwise INFO.
        file_name: Optional log file path. If provided, logs will be written to file.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(logger_name)
    level = logging.DEBUG if is_debug else logging.INFO
    logger.setLevel(level)
    logger.propagate = True  # Allow parent applications to control logging

    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    # Only add console handler if none exists
    if not _has_handler_of_type(logger, logging.StreamHandler):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    # Always add file handler if specified
    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(module_name: str = "") -> logging.Logger:
    """Get a logger instance with the specified module name.

    This function returns a logger that works without requiring explicit setup.
    The logger will propagate to parent loggers, allowing parent applications
    to control logging configuration. If no parent logging is configured,
    the logger will use a NullHandler to prevent warnings.

    Args:
        module_name: The name of the module to be included in the logger name.
                    Empty string returns the root app logger.

    Returns:
        logging.Logger: A logger instance with the specified module name.
    """
    if module_name:
        logger = logging.getLogger(APP_LOGGER_NAME).getChild(module_name)
    else:
        logger = logging.getLogger(APP_LOGGER_NAME)

    # Ensure logger propagates to parent (default behavior, but explicit is better)
    logger.propagate = True

    return logger
