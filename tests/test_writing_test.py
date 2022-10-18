"""
:file: test_writing_test.py

:date: 10/17/2022
:author: Bryan Gillis

Unit tests of writing test reports.
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

from common import TEST_TARBALL_FILENAME
from utility.constants import PUBLIC_DIR, TEST_REPORTS_SUBDIR
from utility.test_writing import TestSummaryWriter


def test_write_summary(project_copy):
    """Unit test of the `TestSummaryWriter` class's __call__ method.

    Parameters
    ----------
    project_copy : str
        Fixture which provides the root directory of a copy of the project
    """

    writer = TestSummaryWriter()
    l_summary_write_output = writer(TEST_TARBALL_FILENAME, project_copy)

    summary_write_output = l_summary_write_output[0]

    # Check that the test name is as expected and the filename is sensible and exists
    test_name_and_filename = summary_write_output.test_name_and_filename
    assert test_name_and_filename.name == "TR-21950be4-0f90-4d36-be01-2a9a507b36cc"
    filename = test_name_and_filename.filename
    assert filename.startswith(TEST_REPORTS_SUBDIR)
    assert filename.endswith(".md")
    assert os.path.isfile(os.path.join(project_copy, PUBLIC_DIR, filename))
