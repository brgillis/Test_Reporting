"""
:file: testing_utility.py

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
import shutil
from typing import TYPE_CHECKING

import pytest

from utility.constants import PUBLIC_DIR, SUMMARY_FILENAME, TESTS_DIR

if TYPE_CHECKING:
    from _pytest.tmpdir import TempdirFactory  # noqa F401

L_FILES_MODIFIED = (os.path.join(PUBLIC_DIR, SUMMARY_FILENAME),
                    )


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


def symlink_contents(src_dir,
                     dest_dir) -> None:
    """Symbolically links the contents of one directory to another directory. Any folders in the source directory
    are re-created in the target directory, with their contents symlinked.

    Parameters
    ----------
    src_dir : str
        The fully-qualified path to the source directory.
    dest_dir : str
        The fully-qualified path to the target directory.
    """

    # Make sure the target directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Get the list of files in the source directory
    l_src_filenames = os.listdir(src_dir)

    # Loop over the files in the source directory
    for src_filename in l_src_filenames:

        # Get the fully-qualified path of the file in the source directory
        qualified_src_filename = os.path.join(src_dir, src_filename)

        # Get the fully-qualified path of the file in the target directory
        qualified_dest_filename = os.path.join(dest_dir, src_filename)

        # If the file is a directory, create a new directory in the target directory, and recursively call this
        # function on it
        if os.path.isdir(qualified_src_filename):
            os.makedirs(qualified_dest_filename, exist_ok=True)
            symlink_contents(src_dir=qualified_src_filename,
                             dest_dir=qualified_dest_filename)
        else:
            # Otherwise, create a symbolic link to the file in the source directory
            os.symlink(qualified_src_filename, qualified_dest_filename)


@pytest.fixture(scope="session")
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
    symlink_contents(rootdir, project_copy_rootdir)

    # Then we'll replace any files we expect to modify with copies, so the original won't be modified
    for filename in L_FILES_MODIFIED:
        src_filename = os.path.join(rootdir, filename)
        dest_filename = os.path.join(project_copy_rootdir, filename)

        # Delete the existing link and replace with a copy
        os.unlink(dest_filename)
        shutil.copy(src_filename, dest_filename)

    return project_copy_rootdir
