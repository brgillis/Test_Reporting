"""
:file: utility/logging.py

:date: 10/18/2022
:author: Bryan Gillis

Module for miscellaneous utility functions.
"""

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger  # noqa F401


def log_entry_exit(logger, level=logging.DEBUG):
    """Decorator which, when applied to a function, will log upon entry/exit of the function.

    Parameters
    ----------
    logger : Logger
    level : int

    Returns
    -------
    Callable
    """

    def func_wrap(func):
        def wrap(*args, **kwargs):
            logger.log(level, f"Entering function `{func.__name__}`.")
            output = func(*args, **kwargs)
            logger.log(level, f"Exiting function `{func.__name__}`.")

            return output

        return wrap

    return func_wrap
