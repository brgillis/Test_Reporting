"""
:file: utility_test.py

:date: 10/18/2022
:author: Bryan Gillis

Unit tests of misc. utility functions.
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

import pytest

from Test_Reporting.testing.common import TEST_TARBALL_FILENAME, TEST_XML_FILENAME
from Test_Reporting.utility.constants import TEST_DATA_DIR
from Test_Reporting.utility.misc import ensure_data_prefix, extract_tarball, get_qualified_path, hash_any

TEST_MAX_LEN = 16


def test_get_qualified_path():
    """Unit test of the `get_qualified_path` method.
    """

    cwd = os.path.normpath(os.getcwd())
    qualified_parent_dir, cur_dir = os.path.split(cwd)

    test_base = "/test/base"
    test_relative_path = "relpath/to/file.txt"
    test_absolute_path = "/path/to/file"

    assert get_qualified_path(test_absolute_path) == test_absolute_path

    assert get_qualified_path(test_relative_path) == os.path.join(cwd, test_relative_path)

    assert get_qualified_path(f"./{test_relative_path}") == os.path.join(cwd, test_relative_path)
    assert get_qualified_path(f"../{test_relative_path}") == os.path.join(qualified_parent_dir, test_relative_path)

    assert get_qualified_path(f"../{cur_dir}") == cwd
    assert get_qualified_path("../") == qualified_parent_dir

    assert get_qualified_path(test_relative_path, base=test_base) == os.path.join(test_base, test_relative_path)


def test_extract_tarball(rootdir, tmpdir):
    """Unit test of the `extract_tarball` method.

    Parameters
    ----------
    rootdir : str
        Fixture which provides the root directory of the project
    rootdir : str
        Fixture which provides a temporary directory for use with testing
    """

    qualified_test_tarball_filename = os.path.join(rootdir, TEST_DATA_DIR, TEST_TARBALL_FILENAME)

    # Try normal execution
    extract_tarball(qualified_test_tarball_filename, tmpdir)
    assert os.path.isfile(os.path.join(tmpdir, TEST_XML_FILENAME))

    with pytest.raises(FileNotFoundError):
        extract_tarball("Bad_filename.tar.gz", tmpdir)

    # Test that we fail when expected with various characters that could spell trouble
    with pytest.raises(ValueError):
        extract_tarball("Bad filename.tar.gz", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball("Bad_filename", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball(r"\Bad_filename.tar.gz", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball("Bad_filename.tar.gz(", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball("Bad_filename.tar.gz{", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball("Bad_filename.tar.gz[", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball("Bad_filename.tar.gz;", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball("Bad_filename.tar.gz&&", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball("Bad_filename.tar.gz|", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball("Bad_filename.tar.gz>", tmpdir)
    with pytest.raises(ValueError):
        extract_tarball("Bad_filename.tar.gz!", tmpdir)


def test_ensure_data_prefix():
    """Unit test of the `ensure_data_prefix` method.
    """
    assert ensure_data_prefix("data/foo") == "data/foo"
    assert ensure_data_prefix("foo") == "data/foo"
    assert ensure_data_prefix("/data/foo") == "/data/foo"
    assert ensure_data_prefix("datafoo") == "data/datafoo"


def test_hash_any():
    """Unit test of the `hash_any` method.
    """

    hash_str = hash_any("foo", max_length=TEST_MAX_LEN)

    assert isinstance(hash_str, str)
    assert len(hash_str) <= TEST_MAX_LEN
