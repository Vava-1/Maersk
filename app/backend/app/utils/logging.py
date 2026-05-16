"""
Enterprise Structured Logging for AfriSwarm.
Uses structlog for structured JSON logs with full traceability.
"""
import structlog
import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps

from ..config import settings


# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if settings.JSON_LOGS else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class AgentLogger:
    """Specialized logger for agent activities with automatic context."""

    def __init__(self, agent_id: str, agent_name: str):
        self.logger = get_logger(f"agent.{agent_id}")
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.context = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "swarm_version": settings.APP_VERSION,
        }

    def _log(self, level: str, message: str, **kwargs):
        extra = {**self.context, **kwargs, "timestamp": datetime.utcnow().isoformat()}
        getattr(self.logger, level)(message, **extra)

    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._log("critical", message, **kwargs)

    def task_start(self, task_id: str, task_type: str, **kwargs):
        self.info(
            f"Task started: {task_type}",
            task_id=task_id,
            task_type=task_type,
            event="task.start",
            **kwargs,
        )

    def task_end(self, task_id: str, result: str, duration_ms: float, **kwargs):
        self.info(
            f"Task completed: {result}",
            task_id=task_id,
            result=result,
            duration_ms=duration_ms,
            event="task.end",
            **kwargs,
        )

    def task_error(self, task_id: str, error: str, **kwargs):
        self.error(
            f"Task failed: {error}",
            task_id=task_id,
            error=error,
            event="task.error",
            **kwargs,
        )

    def healing_action(self, action: str, target: str, result: str, **kwargs):
        self.info(
            f"Healing action: {action} on {target}",
            action=action,
            target=target,
            result=result,
            event="healing.action",
            **kwargs,
        )

    def security_event(self, event_type: str, severity: str, details: Dict[str, Any], **kwargs):
        self.critical(
            f"Security event: {event_type}",
            event_type=event_type,
            severity=severity,
            details=details,
            event="security.event",
            **kwargs,
        )


def log_execution_time(logger: Optional[AgentLogger] = None):
    """Decorator to log function execution time."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                if logger:
                    logger.debug(
                        f"Function executed: {func.__name__}",
                        function=func.__name__,
                        duration_ms=duration,
                    )
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                if logger:
                    logger.error(
                        f"Function failed: {func.__name__}",
                        function=func.__name__,
                        duration_ms=duration,
                        error=str(e),
                        traceback=traceback.format_exc(),
                    )
                raise
        return wrapper
    return decorator
