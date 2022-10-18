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

from conftest import TEST_TARBALL_FILENAME
from utility.constants import TEST_DATA_DIR, TEST_REPORTS_SUBDIR
from utility.test_writing import TestSummaryWriter


def test_write_summary(rootdir):
    """Unit test of the `TestSummaryWriter` class's __call__ method.

    Parameters
    ----------
    rootdir : str
        Fixture which provides the root directory of the project
    """

    # Since the filename is normally expected to be in the "data" dir, but we're working with "test_data" here, we
    # prepend the filename to redirect to that directory
    relative_test_xml_filename = os.path.join("..", TEST_DATA_DIR, TEST_TARBALL_FILENAME)

    writer = TestSummaryWriter()
    l_summary_write_output = writer(relative_test_xml_filename, rootdir)

    summary_write_output = l_summary_write_output[0]

    # Check that the test name is as expected and the filename is sensible
    assert summary_write_output.test_name_and_filename.name == "TR-21950be4-0f90-4d36-be01-2a9a507b36cc"
    assert summary_write_output.test_name_and_filename.filename.startswith(TEST_REPORTS_SUBDIR)
    assert summary_write_output.test_name_and_filename.filename.endswith(".md")
