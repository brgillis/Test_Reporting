"""
:file: conftest.py

:date: 10/12/2022
:author: Bryan Gillis

Utility code for unit tests in this project.
"""
import logging
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
import shutil
from typing import Set, TYPE_CHECKING

import pytest

from Test_Reporting.utility.constants import (DATA_DIR, MANIFEST_FILENAME, PUBLIC_DIR, README_FILENAME,
                                              SUMMARY_FILENAME, TESTS_DIR,
                                              TEST_DATA_DIR, )
from Test_Reporting.utility.product_parsing import parse_xml_product

if TYPE_CHECKING:
    from _pytest.tmpdir import TempdirFactory  # noqa F401
    from collections.abc import Collection  # noqa F401
    from Test_Reporting.utility.report_writing import TestResults

CTI_GAL_MANIFEST_FILENAME = "cti_gal_manifest.json"
CTI_GAL_RESULTS_PRODUCT = "she_observation_cti_gal_validation_test_results_product.xml"

L_FILES_MODIFIED = (os.path.join(PUBLIC_DIR, SUMMARY_FILENAME),
                    os.path.join(PUBLIC_DIR, README_FILENAME),)

S_EXCLUDE = {*L_FILES_MODIFIED, DATA_DIR, TEST_DATA_DIR}


@pytest.fixture(autouse=True)
def log_debug():
    """Fixture to ensure all tests are run at the DEBUG logging level, to catch any bugs in debug log commands.
    """
    logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="session")
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


def symlink_contents(src_dir,
                     dest_dir,
                     s_exclude=None) -> None:
    """Symbolically links the contents of one directory to another directory. Any folders in the source directory
    are re-created in the target directory, with their contents symlinked.

    Parameters
    ----------
    src_dir : str
        The fully-qualified path to the source directory.
    dest_dir : str
        The fully-qualified path to the target directory.
    s_exclude : Collection[str]
        Names of files and directories to be excluded from being symlinked.
    """

    if s_exclude is None:
        s_exclude = {}

    # Make sure the target directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Get the list of files in the source directory
    l_src_filenames = os.listdir(src_dir)

    # Loop over the files in the source directory
    for src_filename in l_src_filenames:

        if src_filename in s_exclude:
            continue

        # Get the fully-qualified path of the file in the source directory
        qualified_src_filename = os.path.join(src_dir, src_filename)

        # Get the fully-qualified path of the file in the target directory
        qualified_dest_filename = os.path.join(dest_dir, src_filename)

        # If the file is a directory, create a new directory in the target directory, and recursively call this
        # function on it
        if os.path.isdir(qualified_src_filename):
            os.makedirs(qualified_dest_filename, exist_ok=True)

            # Construct a set of filenames to exclude in this sub-call
            s_sub_exclude: Set[str] = set()
            for exclude_filename in s_exclude:
                if exclude_filename.startswith(f"{src_filename}/"):
                    s_sub_exclude.add(exclude_filename[len(src_filename) + 1:])

            symlink_contents(src_dir=qualified_src_filename,
                             dest_dir=qualified_dest_filename,
                             s_exclude=s_sub_exclude)
        else:
            # Otherwise, create a symbolic link to the file in the source directory
            os.symlink(qualified_src_filename, qualified_dest_filename)


@pytest.fixture
def project_copy(rootdir, tmpdir_factory):
    """Pytest fixture which creates a copy of the project in a temporary directory for use with unit testing.

    Parameters
    ----------
    rootdir : str
        Pytest fixture providing the root directory of the project.
    tmpdir_factory : TempdirFactory
        Pytest fixture providing a factory to create temporary directories for testing.

    Returns
    -------
    project_copy_rootdir : str
        The fully-qualified path to the created project copy
    """

    project_copy_rootdir = str(tmpdir_factory.mktemp("project_copy"))

    # Start by symlinking the project to the new directory
    os.makedirs(project_copy_rootdir, exist_ok=True)
    symlink_contents(rootdir, project_copy_rootdir, s_exclude=S_EXCLUDE)

    # Then we'll replace any files we expect to modify with copies, so the original won't be modified
    for filename in L_FILES_MODIFIED:
        src_filename = os.path.join(rootdir, filename)
        dest_filename = os.path.join(project_copy_rootdir, filename)

        # Delete the existing link and replace with a copy
        shutil.copy(src_filename, dest_filename)

    # Symlink the contents of the test_data folder to the data folder in the project copy
    test_data_dir = os.path.join(rootdir, TEST_DATA_DIR)
    project_copy_datadir = os.path.join(project_copy_rootdir, DATA_DIR)
    os.makedirs(project_copy_datadir, exist_ok=True)
    symlink_contents(test_data_dir, project_copy_datadir)

    return project_copy_rootdir

@pytest.fixture
def test_manifest(project_copy):
    """Pytest fixture to get the filename of the manifest to use for testing the default builder.

    Returns
    -------
    test_manifest : str
        The fully-qualified path to the testing manifest

    """
    return os.path.join(project_copy, DATA_DIR, MANIFEST_FILENAME)


@pytest.fixture
def cti_gal_manifest(project_copy):
    """Pytest fixture to get the filename of a manifest to use for testing the CTI-Gal builder.

    Returns
    -------
    cti_gal_manifest : str
        The fully-qualified path to the CTI-Gal manifest

    """
    return os.path.join(project_copy, DATA_DIR, CTI_GAL_MANIFEST_FILENAME)


@pytest.fixture
def cti_gal_test_results(rootdir):
    """Pytest fixture providing a mock TestResults object for a CTI-Gal test.

    Returns
    -------
    cti_gal_test_results : TestResults
    """
    return parse_xml_product(os.path.join(rootdir, TEST_DATA_DIR, CTI_GAL_RESULTS_PRODUCT))
