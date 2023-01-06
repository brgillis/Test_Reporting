"""
:file: shear_bias_test.py

:date: 01/06/2023
:author: Bryan Gillis

Unit tests of writing test reports with the shear bias specialization.
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
import re
from typing import List, Set, TYPE_CHECKING

from Test_Reporting.specializations.shear_bias import ShearBiasReportSummaryWriter
from Test_Reporting.testing.common import TEST_SB_TARBALL_FILENAME, TEST_TARBALL_FILENAME
from Test_Reporting.utility.constants import PUBLIC_DIR, TEST_REPORTS_SUBDIR

if TYPE_CHECKING:
    from py.path import local  # noqa F401
    from utility.product_parsing import TestResults  # noqa F401

EX_N_TEST_CASES = 48


def test_write_summary(project_copy):
    """Unit test of the `ReportSummaryWriter` class's `__call__` method.

    Parameters
    ----------
    project_copy : str
        Fixture which provides the root directory of a copy of the project
    """

    writer = ShearBiasReportSummaryWriter()
    test_meta = writer(TEST_SB_TARBALL_FILENAME, project_copy)[0]

    # Check that the test name is as expected and the filename is sensible and exists
    assert test_meta.name == ShearBiasReportSummaryWriter.test_name
    filename = test_meta.filename
    assert filename.startswith(TEST_REPORTS_SUBDIR)
    assert filename.endswith(".md")
    assert os.path.isfile(os.path.join(project_copy, PUBLIC_DIR, filename))

    assert len(test_meta.l_test_case_meta) == EX_N_TEST_CASES

    # Check that each test name is as expected and unique, same for filenames, and that the files exist
    s_test_case_names: Set[str] = set()
    s_test_case_filenames: Set[str] = set()

    n_fig = 0
    n_result = 0
    n_nyi = 0
    n_no_data = 0
    n_na = 0
    for test_case_meta in test_meta.l_test_case_meta:

        # Check for uniqueness
        test_case_name = test_case_meta.name
        if test_case_meta.name in s_test_case_names:
            raise ValueError(f"Duplicate test case name found: {test_case_name}")
        else:
            s_test_case_names.add(test_case_name)

        test_case_filename = test_case_meta.filename
        if test_case_filename in s_test_case_filenames:
            raise ValueError(f"Duplicate test case name found: {test_case_filename}")
        else:
            s_test_case_filenames.add(test_case_filename)

        # Check for proper format for both
        assert test_case_name.startswith("TC-SHE-10001")
        assert test_case_filename.startswith(f"{TEST_REPORTS_SUBDIR}/TC-SHE-10001")
        assert test_case_filename.endswith(".md")

        # Check existence of file
        qualified_test_case_filename = os.path.join(project_copy, PUBLIC_DIR, test_case_filename)
        assert os.path.isfile(qualified_test_case_filename)

        # Read in the file and check the data in it
        l_lines: List[str]
        with open(qualified_test_case_filename, "r") as fi:
            l_lines = fi.readlines()

        assert l_lines[0] == f"# {test_case_name}\n"
        assert l_lines[1] == "\n"
        assert l_lines[2] == "## Table of Contents\n"
        assert l_lines[-1] == "\n"

        # The second-to-last line should be an intercept result, a figure, or "N/A" - count that we get the expected
        # number of each case

        test_line = l_lines[-2]
        figure_regex_match = re.match(r"^!\[(.*)]\(([a-zA-Z0-9./_\-]+)\)\n$", test_line)
        result_regex_match = re.match(r"^[cm]<sub>2</sub> result: \*\*((PASSED)|(FAILED))\*\*\n$", test_line)
        if figure_regex_match:
            # It's a figure, so confirm that it exists
            figure_label, figure_filename = figure_regex_match.groups()

            # Check that the label matches the section label
            assert l_lines[-4].startswith(f"### {figure_label}")

            test_case_path = os.path.split(qualified_test_case_filename)[0]
            assert os.path.isfile(os.path.join(test_case_path, figure_filename))

            n_fig += 1

        elif result_regex_match:

            n_result += 1

        elif test_line == "* This test has not yet been implemented.\n":

            n_nyi += 1

        elif test_line == "* No data is available for this test.\n":

            n_no_data += 1

        else:

            assert test_line == "N/A\n"

            n_na += 1

    assert n_fig == 0
    assert n_result == 40
    assert n_nyi == 0
    assert n_no_data == 8
    assert n_na == 0
