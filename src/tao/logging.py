"""Logging configuration & utilities."""

import logging

from rich.console import Console
from rich.logging import RichHandler

LOG_FORMAT = "%(message)s"
LOG_FORMAT_VERBOSE = "[i]%(name)s[/i] │ %(message)s"
LOG_DATE_FORMAT = "[%X]"
VERBOSITY_MIN = 0
VERBOSITY_MAX = 3

_console = Console()


def setup_logging(verbosity: int) -> None:
    """Define logging level.

    :param verbosity: Accepted values:

                    * 0: no logging except WARNING, ERROR and CRITICAL
                    * 1: INFO level
                    * 2: DEBUG level
                    * 3: DEBUG level with time
    """
    if verbosity < VERBOSITY_MIN or verbosity > VERBOSITY_MAX:
        msg = f"Verbosity must be {VERBOSITY_MIN}-{VERBOSITY_MAX}, got {verbosity}"
        raise ValueError(msg)

    show_level = False
    show_time = False
    log_format = LOG_FORMAT
    if verbosity == VERBOSITY_MIN:
        log_level = logging.WARNING
    elif verbosity == VERBOSITY_MIN + 1:
        log_level = logging.INFO
    elif verbosity == VERBOSITY_MIN + 2:
        log_level = logging.DEBUG
        show_level = True
    elif verbosity == VERBOSITY_MIN + 3:
        log_level = logging.NOTSET
        log_format = LOG_FORMAT_VERBOSE
        show_level = True
        show_time = True

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            RichHandler(
                console=get_console(),
                show_time=show_time,
                show_level=show_level,
                show_path=False,
                markup=True,
                rich_tracebacks=True,
            ),
        ],
    )
    get_logger().setLevel(log_level)


def get_logger() -> logging.Logger:
    """Return project logger."""
    return logging.getLogger("kiln")


def get_console() -> Console:
    """Return project console (rich)."""
    return _console
