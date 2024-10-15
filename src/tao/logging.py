# Copyright 2024, CS GROUP - France, https://www.csgroup.eu/
#
# This file is part of TAO Publisher project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Logging configuration & utilities."""

import logging

from rich.console import Console
from rich.logging import RichHandler

LOG_FORMAT = "%(message)s"
LOG_FORMAT_VERBOSE = "%(name)s │ %(message)s"
LOG_DATE_FORMAT = "[%X]"
VERBOSITY_MIN = 0
VERBOSITY_MAX = 3

_console = Console()


def setup_logging(verbosity: int) -> None:
    """Define logging level.

    Parameters:
        verbosity:

            Accepted values:

            * `0`: no logging except WARNING, ERROR and CRITICAL
            * `1`: INFO level
            * `2`: DEBUG level
            * `3`: DEBUG level with time

    Raises:
        ValueError: verbosity level is <0 or >3
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
                console=_get_console(),
                show_time=show_time,
                show_level=show_level,
                show_path=False,
                markup=False,
                rich_tracebacks=True,
            ),
        ],
    )
    _get_logger().setLevel(log_level)


def _get_logger() -> logging.Logger:
    """Return project logger."""
    return logging.getLogger(__package__)


def _get_console() -> Console:
    """Return project console (rich)."""
    return _console
