"""Logging configuration for the Lausch application."""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure application-wide logging."""
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger("lausch")
    root.setLevel(level)
    root.addHandler(handler)
