"""
:file: report_writing_test.py

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
import re
from typing import List, Set, TYPE_CHECKING

import pytest

from Test_Reporting.testing.common import TEST_TARBALL_FILENAME
from Test_Reporting.utility.constants import PUBLIC_DIR, TEST_REPORTS_SUBDIR
from Test_Reporting.utility.misc import TocMarkdownWriter
from Test_Reporting.utility.report_writing import (DIRECTORY_FILE_EXT, DIRECTORY_FILE_FIGURES_HEADER,
                                                   DIRECTORY_FILE_SEPARATOR, HEADING_DETAILED_RESULTS,
                                                   HEADING_GENERAL_INFO, HEADING_PRODUCT_METADATA,
                                                   HEADING_TEST_CASES, HEADING_TEST_METADATA, HEADING_TEXTFILES,
                                                   MSG_NA, ValTestCaseMeta,
                                                   ReportSummaryWriter, )

if TYPE_CHECKING:
    from py.path import local  # noqa F401
    from utility.product_parsing import TestResults  # noqa F401

EX_N_TEST_CASES = 24

L_COMMON_MOCK_UNPACKED_FILENAMES = ["foo.bar",
                                    "foo2.bar"
                                    "foobar.foobar",
                                    f"foo{DIRECTORY_FILE_EXT}.gz",
                                    "foo.xml",
                                    "foo2.xml",
                                    "dir/subfoo.xml",
                                    "dir/dir/subfoo.xml"]
EX_DIRECTORY_FILENAME = f"foo{DIRECTORY_FILE_EXT}"
EX_EXTRA_DIRECTORY_FILENAME = f"foo2{DIRECTORY_FILE_EXT}"

L_MOCK_DIRECTORY_LABELS_AND_FILENAMES = [("foo", "foo.jpeg"),
                                         ("bar", "bar.png"),
                                         (None, "foobar.jpeg"),
                                         (None, "foobar.png")]

TEST_TITLE = "Test Title"
TEST_NAME = "Test Name"
TEST_CASE_NAME = "Test Case Name"
TEST_CASE_FILENAME = "mock_filename.md"


def _touch_file(qualified_filename: str) -> None:
    """Creates an empty file with the given fully-qualified filename.
    """

    # Make sure the directory containing this file exists
    os.makedirs(os.path.split(qualified_filename)[0], exist_ok=True)

    with open(qualified_filename, "w"):
        pass


def test_write_summary(project_copy):
    """Unit test of the `ReportSummaryWriter` class's __call__ method.

    Parameters
    ----------
    project_copy : str
        Fixture which provides the root directory of a copy of the project
    """

    writer = ReportSummaryWriter()
    test_meta = writer(TEST_TARBALL_FILENAME, project_copy)[0]

    # Check that the test name is as expected and the filename is sensible and exists
    assert test_meta.name == "TR-21950be4-0f90-4d36-be01-2a9a507b36cc"
    filename = test_meta.filename
    assert filename.startswith(TEST_REPORTS_SUBDIR)
    assert filename.endswith(".md")
    assert os.path.isfile(os.path.join(project_copy, PUBLIC_DIR, filename))

    assert len(test_meta.l_test_case_meta) == EX_N_TEST_CASES

    # Check that each test name is as expected and unique, same for filenames, and that the files exist
    s_test_case_names: Set[str] = set()
    s_test_case_filenames: Set[str] = set()
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
        assert test_case_name.startswith("T-SHE-000010-CTI-gal-")
        assert test_case_filename.startswith(f"{TEST_REPORTS_SUBDIR}/T-SHE-000010-CTI-gal-")
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

        # The sixth-to-last line should be a figure, "N/A", or start with "**ERROR**". Check that it matches the
        # expected format and any file that it points to exists

        regex_match = re.match(r"^!\[(.*)]\(([a-zA-Z0-9./_\-]+)\)\n$", l_lines[-6])
        if not regex_match:
            assert l_lines[-6] == f"{MSG_NA}\n"
        else:
            figure_label, figure_filename = regex_match.groups()

            # Check that the label matches the section label
            assert l_lines[-8].startswith(f"### {figure_label}")

            test_case_path = os.path.split(qualified_test_case_filename)[0]
            assert os.path.isfile(os.path.join(test_case_path, figure_filename))

        # We should have no textfiles, so check that we just have the heading and "N/A" here
        assert l_lines[-4].startswith(f"## {HEADING_TEXTFILES}")
        assert l_lines[-2] == f"{MSG_NA}\n"


def test_add_test_case_meta(cti_gal_test_results):
    """ Unit test of the `ReportSummaryWriter._add_test_case_meta` method.

    Parameters
    ----------
    cti_gal_test_results : TestResults
        Pytest fixture providing a mock `TestResults` object.
    """

    # Run the function with an empty writer
    writer = TocMarkdownWriter(TEST_TITLE)
    test_case_results = cti_gal_test_results.l_test_results[0]
    ReportSummaryWriter(TEST_NAME)._add_test_case_meta(writer, test_case_results)

    # Check that a sample of the writer's lines are as expected
    assert writer._l_toc_lines[0] == (f"1. [{HEADING_GENERAL_INFO}](#"
                                      f"{HEADING_GENERAL_INFO.lower().replace(' ', '-')}-0)\n")
    assert writer._l_lines[-1] == "**Result:** PASSED\n\n"


def test_add_test_case_details(cti_gal_test_results):
    """ Unit test of the `ReportSummaryWriter._add_test_case_details` method.

    Parameters
    ----------
    cti_gal_test_results : TestResults
        Pytest fixture providing a mock `TestResults` object.
    """

    # Run the function with an empty writer
    writer = TocMarkdownWriter(TEST_TITLE)
    test_case_results = cti_gal_test_results.l_test_results[0]
    ReportSummaryWriter(TEST_NAME)._add_test_case_details(writer, test_case_results)

    # Check that a sample of the writer's lines are as expected
    assert writer._l_toc_lines[0] == (f"1. [{HEADING_DETAILED_RESULTS}](#"
                                      f"{HEADING_DETAILED_RESULTS.lower().replace(' ', '-')}-0)\n")
    assert writer._l_lines[-1] == "\n```\n\n"


@pytest.fixture
def mock_unpacked_dir(tmpdir):
    """A Pytest fixture providing a directory containing a mock set of unpacked files.

    Parameters
    ----------
    tmpdir : local
        pytest's `tmpdir` fixture

    Returns
    -------
    mock_unpacked_dir : str
        Fully-qualified path to the directory containing mock unpacked data.
    """

    # Create empty files with the list of common filenames
    for filename in L_COMMON_MOCK_UNPACKED_FILENAMES:
        _touch_file(os.path.join(tmpdir, filename))

    return tmpdir.strpath


def test_find_directory_filename(mock_unpacked_dir):
    """Unit test of the `ReportSummaryWriter.find_directory_filename` method.

    Parameters
    ----------
    mock_unpacked_dir : str
        Pytest fixture providing the fully-qualified filename of a directory prepared with some mock files. This is
        set up so that none of these files initially have the expected directory extension.
    """

    # As initially set up, there shouldn't be a directory, so check we get the expected exception
    with pytest.raises(FileNotFoundError):
        ReportSummaryWriter.find_directory_filename(mock_unpacked_dir)

    # Add a file with an appropriate filename and check that we find it
    qualified_directory_filename = os.path.join(mock_unpacked_dir, EX_DIRECTORY_FILENAME)
    _touch_file(qualified_directory_filename)
    assert ReportSummaryWriter.find_directory_filename(mock_unpacked_dir) == qualified_directory_filename

    # Add an extra file with an appropriate filename and check that we get the expected exception from having too
    # many candidate files
    _touch_file(os.path.join(mock_unpacked_dir, EX_EXTRA_DIRECTORY_FILENAME))
    with pytest.raises(ValueError):
        ReportSummaryWriter.find_directory_filename(mock_unpacked_dir)


def test_find_product_filenames(mock_unpacked_dir):
    """Unit test of the `ReportSummaryWriter._find_product_filenames` method.

    Parameters
    ----------
    mock_unpacked_dir : str
        Pytest fixture providing the fully-qualified filename of a directory prepared with some mock files. This is
        set up to have multiple possible product files, some being in subdirs.
    """

    l_product_filenames = ReportSummaryWriter(TEST_NAME)._find_product_filenames(mock_unpacked_dir)

    assert "foo.xml" in l_product_filenames
    assert "foo2.xml" in l_product_filenames
    assert "dir/subfoo.xml" in l_product_filenames
    assert "dir/dir/subfoo.xml" in l_product_filenames
    assert len(l_product_filenames) == 4

    # Check we get an expected exception with an empty dir
    qualified_empty_dir = os.path.join(mock_unpacked_dir, "empty_dir")
    os.makedirs(qualified_empty_dir, exist_ok=True)
    with pytest.raises(ValueError):
        ReportSummaryWriter(TEST_NAME)._find_product_filenames(qualified_empty_dir)


@pytest.fixture
def mock_directory_file(tmpdir):
    """A Pytest fixture providing a mock directory file.

    Parameters
    ----------
    tmpdir : local

    Returns
    -------
    mock_directory_file : str
        Fully-qualified path to the generated mock directory file.
    """

    qualified_directory_filename = os.path.join(tmpdir, f"mock_dir{DIRECTORY_FILE_EXT}")

    with open(qualified_directory_filename, 'w') as fo:
        fo.write(f"{DIRECTORY_FILE_FIGURES_HEADER}\n")
        for label, filename in L_MOCK_DIRECTORY_LABELS_AND_FILENAMES:
            if label is None:
                fo.write(f"{filename}\n")
            else:
                fo.write(f"{label}{DIRECTORY_FILE_SEPARATOR}{filename}\n")

    return qualified_directory_filename


def test_read_figure_labels_and_filenames(mock_directory_file):
    """Unit test of the `ReportSummaryWriter.read_figure_labels_and_filenames` method.

    Parameters
    ----------
    mock_directory_file : str
        Pytest fixture providing the filename of a mock directory file set up for this test.
    """

    l_labels_and_filenames = ReportSummaryWriter.read_ana_files_labels_and_filenames(mock_directory_file)

    assert l_labels_and_filenames == L_MOCK_DIRECTORY_LABELS_AND_FILENAMES


def test_write_product_metadata(cti_gal_test_results):
    """ Unit test of the `ReportSummaryWriter._write_product_metadata` method.

    Parameters
    ----------
    cti_gal_test_results : TestResults
        Pytest fixture providing a mock `TestResults` object.
    """

    # Run the function with an empty writer
    writer = TocMarkdownWriter(TEST_TITLE)
    ReportSummaryWriter(TEST_NAME)._add_product_metadata(writer, cti_gal_test_results)

    # Check that a sample of the writer's lines are as expected
    assert writer._l_toc_lines[0] == (f"1. [{HEADING_PRODUCT_METADATA}](#"
                                      f"{HEADING_PRODUCT_METADATA.lower().replace(' ', '-')}-0)\n")
    assert writer._l_lines[-1] == "**Creation Date and Time:** 3 Dec, 2021 at 11:24:43.408000\n\n"


def test_write_test_metadata(cti_gal_test_results):
    """ Unit test of the `ReportSummaryWriter._write_test_metadata` method.

    Parameters
    ----------
    cti_gal_test_results : TestResults
        Pytest fixture providing a mock `TestResults` object.
    """

    # Run the function with an empty writer
    writer = TocMarkdownWriter(TEST_TITLE)
    ReportSummaryWriter(TEST_NAME)._add_test_metadata(writer, cti_gal_test_results)

    # Check that a sample of the writer's lines are as expected
    assert writer._l_toc_lines[0] == (f"1. [{HEADING_TEST_METADATA}](#"
                                      f"{HEADING_TEST_METADATA.lower().replace(' ', '-')}-0)\n")
    assert writer._l_lines[-1] == "**Number of Exposures:** 4\n\n"


def test_write_test_case_table(cti_gal_test_results):
    """ Unit test of the `ReportSummaryWriter._write_test_case_table` method.

    Parameters
    ----------
    cti_gal_test_results : TestResults
        Pytest fixture providing a mock `TestResults` object.
    """

    # Make a mock list of test case meta
    l_test_case_meta = [
        ValTestCaseMeta(name=TEST_CASE_NAME, filename=f"{TEST_REPORTS_SUBDIR}/{TEST_CASE_FILENAME}", passed=True)]

    # Run the function with an empty writer
    writer = TocMarkdownWriter(TEST_TITLE)
    ReportSummaryWriter(TEST_NAME)._add_test_case_table(writer, cti_gal_test_results, l_test_case_meta)

    # Check that a sample of the writer's lines are as expected
    assert writer._l_toc_lines[0] == (f"1. [{HEADING_TEST_CASES}](#"
                                      f"{HEADING_TEST_CASES.lower().replace(' ', '-')}-0)\n")
    assert writer._l_lines[-1] == f"| [{TEST_CASE_NAME}]({TEST_CASE_FILENAME.replace('.md', '.html')}) | PASSED |\n"
