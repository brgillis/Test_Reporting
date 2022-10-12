"""
:file: utility.py

:date: 10/12/2022
:author: Bryan Gillis

Utility code for unit tests in this project.
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

import os

import pytest

from utility.constants import TESTS_DIR


@pytest.fixture
def rootdir():
    """Pytest fixture to get the root directory of the project.

    Returns
    -------
    rootdir : str
        The root directory of the project.

    """
    cwd = os.getcwd()

    # Check if we're in the tests directory, and if so, the rootdir will be one level up
    if os.path.split(cwd)[-1] == TESTS_DIR:
        rootdir = os.path.join(cwd, "..")
    else:
        rootdir = cwd

    return rootdir
