"""
:file: summary_test.py

:date: 10/13/2022
:author: Bryan Gillis

Unit tests of updating the SUMMARY.md file
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

from testing.common import L_TEST_META
from utility.constants import HEADING_TOC, PUBLIC_DIR, README_FILENAME, SUMMARY_FILENAME, TEST_REPORT_SUMMARY_FILENAME
from utility.summary_files import build_test_report_summary, update_readme, update_summary

EX_TEST_SUMMARY_STR = f"* [Test Reports]({TEST_REPORT_SUMMARY_FILENAME})\n"
EX_TEST_STR_1 = "  * [T1](T1.md)\n"
EX_TEST_CASE_STR_1_1 = "    * [TC1-1](TC1-1.md)\n"
EX_TEST_STR_2 = "  * [T2](T2a.md)\n"
EX_TEST_CASE_STR_2_1 = "    * [TC2-1](TC2-1.md)\n"
EX_TEST_CASE_STR_2_2 = "    * [TC2-2](TC2-2.md)\n"

EX_TR_TEST_STR_1 = "| [T1](T1.html) | -1 | -1 |\n"
EX_TR_TEST_STR_2 = "| [T2](T2a.html) | 1 | 2 |\n"


def test_update_summary(project_copy):
    """Tests updating the public SUMMARY.md file.

    Parameters
    ----------
    project_copy : str
        Pytest fixture providing the fully-qualified path to a copy of the project created for testing purposes.
    """

    update_summary(test_report_summary_filename=TEST_REPORT_SUMMARY_FILENAME,
                   l_test_meta=L_TEST_META,
                   rootdir=project_copy)

    qualified_summary_filename = os.path.join(project_copy, PUBLIC_DIR, SUMMARY_FILENAME)
    assert os.path.isfile(qualified_summary_filename)

    # Check that the file contains the expected content
    with open(qualified_summary_filename, "r") as fi:
        l_lines = fi.readlines()
    assert l_lines[-6] == EX_TEST_SUMMARY_STR
    assert l_lines[-5] == EX_TEST_STR_1
    assert l_lines[-4] == EX_TEST_CASE_STR_1_1
    assert l_lines[-3] == EX_TEST_STR_2
    assert l_lines[-2] == EX_TEST_CASE_STR_2_1
    assert l_lines[-1] == EX_TEST_CASE_STR_2_2


def test_update_readme(project_copy):
    """Tests updating the README.md file.

    Parameters
    ----------
    project_copy : str
    """

    # Update the summary as with the other test, so we can check that the same test strings get added to the readme
    update_summary(test_report_summary_filename=TEST_REPORT_SUMMARY_FILENAME,
                   l_test_meta=L_TEST_META,
                   rootdir=project_copy)

    update_readme(rootdir=project_copy)

    qualified_readme_filename = os.path.join(project_copy, PUBLIC_DIR, README_FILENAME)
    assert os.path.isfile(qualified_readme_filename)

    # Check that the file contains the expected content
    with open(qualified_readme_filename, "r") as fi:
        l_lines = fi.readlines()
    assert f"{HEADING_TOC}\n" in l_lines
    assert l_lines[-6] == EX_TEST_SUMMARY_STR
    assert l_lines[-5] == EX_TEST_STR_1
    assert l_lines[-4] == EX_TEST_CASE_STR_1_1
    assert l_lines[-3] == EX_TEST_STR_2
    assert l_lines[-2] == EX_TEST_CASE_STR_2_1
    assert l_lines[-1] == EX_TEST_CASE_STR_2_2


def test_build_test_report_summary(project_copy):
    """Tests generating the test report summary.

    Parameters
    ----------
    project_copy : str
    """

    build_test_report_summary(test_report_summary_filename=TEST_REPORT_SUMMARY_FILENAME,
                              l_test_meta=L_TEST_META,
                              rootdir=project_copy)

    qualified_test_report_summary_filename = os.path.join(project_copy, PUBLIC_DIR, TEST_REPORT_SUMMARY_FILENAME)
    assert os.path.isfile(qualified_test_report_summary_filename)

    # Check that the file contains the expected content
    with open(qualified_test_report_summary_filename, "r") as fi:
        l_lines = fi.readlines()
    assert l_lines[-4] == EX_TR_TEST_STR_1
    assert l_lines[-3] == EX_TR_TEST_STR_2
