"""Centralised logging configuration with Loki integration."""
import logging
import json
import os
from logging.handlers import QueueHandler
import socket
try:
    from pythonjsonlogger.json import JsonFormatter
except ImportError:
    from pythonjsonlogger.jsonlogger import JsonFormatter
from datetime import datetime, timezone


class LokiLogHandler(logging.Handler):
    """Custom handler to send logs to Loki."""

    def __init__(self, loki_url: str, labels: dict):
        super().__init__()
        self.loki_url = loki_url
        self.labels = labels
        self.session = None
        try:
            import requests
            self.session = requests
        except ImportError:
            pass  # Fallback if requests not available

    def emit(self, record):
        """Send log record to Loki."""
        try:
            if not self.session:
                return

            log_entry = self.format(record)
            timestamp_ns = int(record.created * 1e9)
            
            # Build Loki log payload
            payload = {
                "streams": [
                    {
                        "stream": self.labels,
                        "values": [
                            [str(timestamp_ns), log_entry]
                        ]
                    }
                ]
            }

            # POST to Loki
            self.session.post(
                f"{self.loki_url}/loki/api/v1/push",
                json=payload,
                timeout=2
            )
        except Exception:
            pass  # Silently ignore logging errors to avoid loops



def create_json_formatter():
    """Create JSON formatter with custom fields."""
    formatter = JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    # Wrap with custom add_fields
    original_add_fields = formatter.add_fields

    def add_fields_wrapper(log_record, record, message_dict):
        original_add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['hostname'] = socket.gethostname()
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id

    formatter.add_fields = add_fields_wrapper
    return formatter


def setup_logging(app=None, loki_enabled: bool = None):
    """Configure logging with Loki integration.

    Args:
        app: Flask app instance (optional)
        loki_enabled: Override auto-detection (checks env var LOKI_ENABLED)
    """
    if loki_enabled is None:
        loki_enabled = os.getenv('LOKI_ENABLED', 'false').lower() == 'true'

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = create_json_formatter()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Loki handler (if enabled)
    if loki_enabled:
        loki_url = os.getenv('LOKI_URL', 'http://localhost:3100')
        loki_handler = LokiLogHandler(
            loki_url=loki_url,
            labels={
                'app': 'sgdi-sistema-legado',
                'environment': os.getenv('ENVIRONMENT', 'development'),
                'service': os.getenv('SERVICE_NAME', 'main'),
            }
        )
        loki_handler.setLevel(logging.INFO)
        loki_handler.setFormatter(formatter)
        root_logger.addHandler(loki_handler)

    # Flask-specific logging
    if app:
        app.logger.setLevel(logging.INFO)
        for handler in app.logger.handlers[:]:
            app.logger.removeHandler(handler)
        app.logger.addHandler(console_handler)
        if loki_enabled:
            app.logger.addHandler(loki_handler)

    return root_logger


def get_logger(name: str):
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


def log_with_context(logger, level, message, **context):
    """Log with additional context fields (e.g. request_id)."""
    extra = {'request_id': context.get('request_id', 'N/A')}
    context_msg = " | ".join(f"{k}={v}" for k, v in context.items())
    full_msg = f"{message} | {context_msg}" if context_msg else message

    if level == 'info':
        logger.info(full_msg, extra=extra)
    elif level == 'warning':
        logger.warning(full_msg, extra=extra)
    elif level == 'error':
        logger.error(full_msg, extra=extra, exc_info=True)
    elif level == 'debug':
        logger.debug(full_msg, extra=extra)

