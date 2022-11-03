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
from typing import Set, TYPE_CHECKING

import pytest

from testing.common import TEST_TARBALL_FILENAME
from utility.constants import PUBLIC_DIR, TEST_REPORTS_SUBDIR
from utility.test_writing import DIRECTORY_EXT, DIRECTORY_FIGURES_HEADER, DIRECTORY_SEPARATOR, TestSummaryWriter

if TYPE_CHECKING:
    from py.path import local  # noqa F401

EX_N_TEST_CASES = 24

L_COMMON_MOCK_UNPACKED_FILENAMES = ["foo.bar",
                                    "foo2.bar"
                                    "foobar.foobar",
                                    f"foo{DIRECTORY_EXT}.gz"]
EX_DIRECTORY_FILENAME = f"foo{DIRECTORY_EXT}"
EX_EXTRA_DIRECTORY_FILENAME = f"foo2{DIRECTORY_EXT}"

L_MOCK_DIRECTORY_LABELS_AND_FILENAMES = [("foo", "foo.jpeg"),
                                         ("bar", "bar.png"),
                                         (None, "foobar.jpeg"),
                                         (None, "foobar.png")]


def _touch_file(qualified_filename: str) -> None:
    """Creates an empty file with the give fully-qualified filename.
    """
    with open(qualified_filename, "w"):
        pass


def test_write_summary(project_copy):
    """Unit test of the `TestSummaryWriter` class's __call__ method.

    Parameters
    ----------
    project_copy : str
        Fixture which provides the root directory of a copy of the project
    """

    writer = TestSummaryWriter()
    l_test_meta = writer(TEST_TARBALL_FILENAME, project_copy)

    test_meta = l_test_meta[0]

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
        with open(qualified_test_case_filename, "r") as fi:
            l_lines = fi.readlines()
            assert l_lines[0] == f"# {test_case_name}\n"
            assert l_lines[1] == "\n"
            assert l_lines[2] == "## Table of Contents\n"
            # We don't do in-depth checks pas this, as we don't want to make it too burdensome to update this test
            # whenever the format is changed


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
    """Unit test of the `TestSummaryWriter.find_directory_filename` method.

    Parameters
    ----------
    mock_unpacked_dir : str
        Pytest fixture providing the fully-qualified filename of a directory prepared with some mock files. This is
        set up so that none of these files initially have the expected directory extension.
    """

    # As initially set up, there shouldn't be a directory, so check we get the expected exception
    with pytest.raises(FileNotFoundError):
        TestSummaryWriter.find_directory_filename(mock_unpacked_dir)

    # Add a file with an appropriate filename and check that we find it
    qualified_directory_filename = os.path.join(mock_unpacked_dir, EX_DIRECTORY_FILENAME)
    _touch_file(qualified_directory_filename)
    assert TestSummaryWriter.find_directory_filename(mock_unpacked_dir) == qualified_directory_filename

    # Add an extra file with an appropriate filename and check that we get the expected exception from having too
    # many candidate files
    _touch_file(os.path.join(mock_unpacked_dir, EX_EXTRA_DIRECTORY_FILENAME))
    with pytest.raises(ValueError):
        TestSummaryWriter.find_directory_filename(mock_unpacked_dir)


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

    qualified_directory_filename = os.path.join(tmpdir, f"mock_dir{DIRECTORY_EXT}")

    with open(qualified_directory_filename, 'w') as fo:
        fo.write(f"{DIRECTORY_FIGURES_HEADER}\n")
        for label, filename in L_MOCK_DIRECTORY_LABELS_AND_FILENAMES:
            if label is None:
                fo.write(f"{filename}\n")
            else:
                fo.write(f"{label}{DIRECTORY_SEPARATOR}{filename}\n")

    return qualified_directory_filename


def test_read_figure_labels_and_filenames(mock_directory_file):
    """Unit test of the `TestSummaryWriter.read_figure_labels_and_filenames` method.

    Parameters
    ----------
    mock_directory_file : str
        Pytest fixture providing the filename of a mock directory file set up for this test.
    """

    l_labels_and_filenames = TestSummaryWriter.read_figure_labels_and_filenames(mock_directory_file)

    assert l_labels_and_filenames == L_MOCK_DIRECTORY_LABELS_AND_FILENAMES
