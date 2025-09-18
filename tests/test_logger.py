"""
Unit tests for logger utility
"""
import pytest
import sys
import os
import logging
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.logger import setup_module_logger, get_logger


class TestLoggerSetup:
    """Test logger setup functionality"""

    def test_setup_module_logger(self):
        """Test setting up a module logger"""
        logger = setup_module_logger("test.module")

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_get_logger(self):
        """Test getting logger instance"""
        logger = get_logger("test.logger")

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.logger"

    def test_logger_singleton(self):
        """Test that same logger name returns same instance"""
        logger1 = get_logger("test.singleton")
        logger2 = get_logger("test.singleton")

        assert logger1 is logger2

    def test_logger_hierarchy(self):
        """Test logger hierarchy"""
        parent_logger = get_logger("test")
        child_logger = get_logger("test.child")

        assert child_logger.name == "test.child"
        assert parent_logger.name == "test"

    def test_logger_effective_level(self):
        """Test logger effective level"""
        logger = get_logger("test.level")

        # Should inherit from root logger or have default level
        assert logger.getEffectiveLevel() in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]


class TestLoggerConfiguration:
    """Test logger configuration"""

    def test_logger_file_output(self):
        """Test logger writes to file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            # Create logger that writes to file
            logger = setup_module_logger("test.file", log_file=str(log_file))

            # Log a message
            test_message = "Test log message"
            logger.info(test_message)

            # Check file was created and contains message
            assert log_file.exists()
            content = log_file.read_text()
            assert test_message in content

    def test_logger_console_output(self):
        """Test logger outputs to console"""
        logger = setup_module_logger("test.console")

        # This is harder to test directly, but we can check logger has handlers
        assert len(logger.handlers) > 0

    def test_logger_formatting(self):
        """Test logger message formatting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "format_test.log"

            logger = setup_module_logger("test.format", log_file=str(log_file))
            logger.info("Test message with %s", "parameter")

            content = log_file.read_text()
            # Should contain timestamp, level, logger name, and message
            assert "INFO" in content
            assert "test.format" in content
            assert "Test message with parameter" in content


class TestLoggerLevels:
    """Test different logging levels"""

    def test_debug_level(self):
        """Test debug level logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "debug_test.log"

            logger = setup_module_logger("test.debug", log_file=str(log_file))
            logger.setLevel(logging.DEBUG)

            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")

            content = log_file.read_text()
            assert "DEBUG" in content
            assert "Debug message" in content
            assert "INFO" in content
            assert "Info message" in content
            assert "WARNING" in content
            assert "Warning message" in content

    def test_info_level(self):
        """Test info level logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "info_test.log"

            logger = setup_module_logger("test.info", log_file=str(log_file))
            logger.setLevel(logging.INFO)

            logger.debug("Debug message")  # Should not appear
            logger.info("Info message")
            logger.warning("Warning message")

            content = log_file.read_text()
            assert "DEBUG" not in content
            assert "Debug message" not in content
            assert "INFO" in content
            assert "Info message" in content
            assert "WARNING" in content
            assert "Warning message" in content

    def test_error_level(self):
        """Test error level logging"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "error_test.log"

            logger = setup_module_logger("test.error", log_file=str(log_file))
            logger.setLevel(logging.ERROR)

            logger.info("Info message")  # Should not appear
            logger.warning("Warning message")  # Should not appear
            logger.error("Error message")

            content = log_file.read_text()
            assert "INFO" not in content
            assert "Info message" not in content
            assert "WARNING" not in content
            assert "Warning message" not in content
            assert "ERROR" in content
            assert "Error message" in content


class TestLoggerExceptionHandling:
    """Test logger exception handling"""

    def test_exception_logging(self):
        """Test logging exceptions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "exception_test.log"

            logger = setup_module_logger("test.exception", log_file=str(log_file))

            try:
                raise ValueError("Test exception")
            except Exception as e:
                logger.exception("Exception occurred")

            content = log_file.read_text()
            assert "Exception occurred" in content
            assert "ValueError" in content
            assert "Test exception" in content


if __name__ == "__main__":
    pytest.main([__file__])