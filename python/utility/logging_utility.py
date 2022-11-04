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

import inspect
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger  # noqa F401


def get_function_name(depth=1):
    """Returns the name of the enclosing function at a desired depth. Code copied and extended from
    https://stackoverflow.com/a/67488637/5099457.

    Parameters
    ----------
    depth : int, default=1
        Int >=0 providing the name of the corresponding function in the stack. If depth==0, the name of this function
        will always be returned. If depth==1, the name of the function calling this function will be returned. If
        depth==2, the name of the function calling the function calling this function will be returned, etc.

    Returns
    -------
    function_name : str
        The name of the function calling this function (or the corresponding in a  higher frame depth>1)
    """
    return inspect.stack()[depth].function


def log_function_action(logger, action, level=logging.DEBUG, depth=1):
    """Logs an action relating to the function calling this, using the name of that function.

    Parameters
    ----------
    logger : Logger
        The logger to use to log this action.
    action : str
        The action to log that we're performing (e.g. "Entering" or "Exiting")
    level : int, default=logging.DEBUG
        The level to log at (default DEBUG)
    depth : int, default=1
    """
    logger.log(level, f"{action} function {get_function_name(depth + 1)}.")


def log_function_entry(logger, level=logging.DEBUG, depth=1):
    """Logs entry of the function which calls this.

    Parameters
    ----------
    logger : Logger
    level : int, default=logging.DEBUG
    depth : int, default=1
    """
    log_function_action(logger=logger,
                        action="Entering",
                        level=level,
                        depth=depth + 1)


def log_function_exit(logger, level=logging.DEBUG, depth=1):
    """Logs exit of the function which calls this.

    Parameters
    ----------
    logger : Logger
    level : int, default=logging.DEBUG
    depth : int, default=1
    """
    log_function_action(logger=logger,
                        action="Exiting",
                        level=level,
                        depth=depth + 1)
