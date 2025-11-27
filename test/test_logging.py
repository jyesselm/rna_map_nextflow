import logging
import os

from rna_map import logger

app_logger = logger.setup_applevel_logger()


def test_logging(caplog):
    """Test basic logging functionality."""
    app_logger.info("test")
    assert caplog.record_tuples[0][0] == "rna-map"
    assert caplog.record_tuples[0][-1] == "test"


def test_logging_2(caplog):
    """Test module-specific logger."""
    log = logger.get_logger("TEST")
    log.info("test")
    assert caplog.record_tuples[0][0] == "rna-map.TEST"
    assert caplog.record_tuples[0][-1] == "test"


def test_write_to_file():
    """Test file logging."""
    app_logger = logger.setup_applevel_logger(file_name="rna_map.log")
    app_logger.info("test")
    assert os.path.isfile("rna_map.log")
    os.remove("rna_map.log")


def test_get_logger_without_setup(caplog):
    """Test that get_logger works without explicit setup (library-friendly)."""
    # Get logger without calling setup - should work via propagation
    log = logger.get_logger("LIBRARY_TEST")
    log.info("test message")
    # Should propagate to root logger if configured
    assert len(caplog.record_tuples) > 0


def test_logger_propagation():
    """Test that loggers propagate to parent loggers."""
    log = logger.get_logger("PROPAGATION_TEST")
    assert log.propagate is True, "Loggers should propagate by default"


def test_no_duplicate_handlers():
    """Test that setup functions don't create duplicate handlers."""
    # Clean up any existing handlers first
    app_logger = logging.getLogger("rna-map")
    for handler in list(app_logger.handlers):
        app_logger.removeHandler(handler)
    
    # Setup logging twice
    logger.setup_applevel_logger()
    logger.setup_applevel_logger()
    
    # Count StreamHandlers that are not FileHandlers
    console_handlers = [
        h for h in app_logger.handlers
        if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
    ]
    # Should only have one console StreamHandler
    assert len(console_handlers) == 1, "Should not create duplicate console StreamHandlers"


def test_is_logging_configured():
    """Test the is_logging_configured utility function."""
    # Before setup, should return False (or True if root logger has handlers)
    # After setup, should return True
    logger.setup_applevel_logger()
    assert logger.is_logging_configured() is True


def test_library_usage_with_parent_logger(caplog):
    """Test library usage when parent application configures logging."""
    # Simulate parent application setting up root logger
    root_logger = logging.getLogger()
    root_handler = logging.StreamHandler()
    root_handler.setFormatter(logging.Formatter("%(name)s: %(message)s"))
    root_logger.addHandler(root_handler)
    root_logger.setLevel(logging.INFO)
    
    # Now get a library logger - should propagate to parent
    lib_logger = logger.get_logger("PARENT_TEST")
    lib_logger.info("library message")
    
    # Should appear in caplog via propagation
    assert len(caplog.record_tuples) > 0
    
    # Cleanup
    root_logger.removeHandler(root_handler)
