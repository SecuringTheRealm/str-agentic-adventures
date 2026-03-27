"""
Tests for structured JSON logging configuration.
"""

import json
import logging
from io import StringIO

from pythonjsonlogger.json import JsonFormatter


class TestJsonLoggingFormatter:
    """Tests that the JSON logging formatter produces valid structured output."""

    def _make_handler(self, stream: StringIO) -> logging.StreamHandler:
        handler = logging.StreamHandler(stream)
        fmt = "%(asctime)s %(name)s %(levelname)s %(message)s %(module)s %(funcName)s"
        handler.setFormatter(JsonFormatter(fmt=fmt))
        return handler

    def test_log_output_is_valid_json(self):
        """Each log line must be parseable as JSON."""
        stream = StringIO()
        handler = self._make_handler(stream)
        logger = logging.getLogger("test_json_valid")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        try:
            logger.info("hello world")
        finally:
            logger.removeHandler(handler)

        output = stream.getvalue().strip()
        record = json.loads(output)
        assert record["message"] == "hello world"

    def test_log_contains_required_fields(self):
        """Structured log records must include level, logger name, and message."""
        stream = StringIO()
        handler = self._make_handler(stream)
        logger = logging.getLogger("test_json_fields")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        try:
            logger.warning("check fields")
        finally:
            logger.removeHandler(handler)

        record = json.loads(stream.getvalue().strip())
        assert record["levelname"] == "WARNING"
        assert record["name"] == "test_json_fields"
        assert record["message"] == "check fields"

    def test_exception_info_included(self):
        """Exception info must be serialised into the JSON record."""
        stream = StringIO()
        handler = self._make_handler(stream)
        logger = logging.getLogger("test_json_exc")
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        try:
            try:
                raise ValueError("boom")
            except ValueError:
                logger.exception("caught error")
        finally:
            logger.removeHandler(handler)

        record = json.loads(stream.getvalue().strip())
        assert record["message"] == "caught error"
        assert "exc_info" in record
        assert "ValueError" in record["exc_info"]

    def test_root_logger_uses_json_formatter(self):
        """The root logger configured in main.py must use the JSON formatter."""
        from app.main import configure_logging

        configure_logging()

        root_logger = logging.getLogger()
        assert root_logger.handlers, "Root logger must have at least one handler"
        handler = root_logger.handlers[0]
        assert isinstance(
            handler.formatter, JsonFormatter
        ), "Root logger handler formatter must be JsonFormatter"
