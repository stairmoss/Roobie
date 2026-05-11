"""
Roobie Logger
Structured logging with file and console output.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class RoobieLogger:
    """Structured logger for Roobie operations."""

    def __init__(self, name: str = "roobie", log_dir: str = "~/.roobie/logs",
                 level: str = "INFO"):
        self.log_dir = Path(log_dir).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.logger.handlers.clear()

        # File handler
        log_file = self.log_dir / f"roobie_{datetime.now().strftime('%Y%m%d')}.log"
        fh = logging.FileHandler(str(log_file))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        self.logger.addHandler(fh)

        # Console handler (errors only to avoid Rich conflicts)
        ch = logging.StreamHandler(sys.stderr)
        ch.setLevel(logging.WARNING)
        ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        self.logger.addHandler(ch)

    def debug(self, msg: str, **kwargs):
        self.logger.debug(msg, extra=kwargs)

    def info(self, msg: str, **kwargs):
        self.logger.info(msg, extra=kwargs)

    def warning(self, msg: str, **kwargs):
        self.logger.warning(msg, extra=kwargs)

    def error(self, msg: str, **kwargs):
        self.logger.error(msg, extra=kwargs)

    def stage(self, stage_name: str, status: str, details: str = ""):
        """Log a workflow stage transition."""
        self.logger.info(f"STAGE [{stage_name}] {status} {details}".strip())

    def metric(self, name: str, value: float, unit: str = ""):
        """Log a performance metric."""
        self.logger.info(f"METRIC {name}={value}{unit}")


_logger: Optional[RoobieLogger] = None


def get_logger(name: str = "roobie") -> RoobieLogger:
    """Get or create the global logger."""
    global _logger
    if _logger is None:
        _logger = RoobieLogger(name)
    return _logger
