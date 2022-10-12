"""
:file: constants_test.py

:date: 10/12/2022
:author: Bryan Gillis

Unit tests of reading in .json manifest files.
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

from .testing_utility import rootdir  # noqa F401


def test_files_exist(rootdir):
    """Unit test that checks that all filenames and directories defined in the constants correspond to actual files and
    directories in this project.

    Parameters
    ----------
    rootdir : str
        Fixture which provides the root directory of the project
    """

    pass
