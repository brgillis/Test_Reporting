"""
:file: dataproc_test.py

:date: 01/23/2023
:author: Bryan Gillis

Unit tests of writing test reports with the DataProc specialization.
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
from typing import TYPE_CHECKING

from Test_Reporting.specializations.dataproc import DataProcReportSummaryWriter
from Test_Reporting.testing.common import TEST_DP_RESULTS_FILENAME
from Test_Reporting.utility.constants import PUBLIC_DIR, TEST_REPORTS_SUBDIR

EX_N_TEST_CASES = 4


def test_write_summary(project_copy):
    """Unit test of the `ReportSummaryWriter` class's `__call__` method.

    Parameters
    ----------
    project_copy : str
        Fixture which provides the root directory of a copy of the project
    """

    writer = DataProcReportSummaryWriter()
    test_meta = writer(TEST_DP_RESULTS_FILENAME, project_copy)[0]

    # Check that the test name is as expected and the filename is sensible and exists
    assert test_meta.name == DataProcReportSummaryWriter.test_name
    filename = test_meta.filename
    assert filename.startswith(TEST_REPORTS_SUBDIR)
    assert filename.endswith(".md")
    assert os.path.isfile(os.path.join(project_copy, PUBLIC_DIR, filename))

    assert len(test_meta.l_test_case_meta) == EX_N_TEST_CASES
