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

from test_data.common import TEST_TARBALL_FILENAME, TEST_XML_FILENAME
from utility.constants import TEST_DATA_DIR
from utility.misc import extract_tarball, hash_any


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


def test_hash_any():
    """Unit test of the `hash_any` method.
    """

    TEST_MAX_LEN = 16

    hash_str = hash_any("foo", max_length=TEST_MAX_LEN)

    assert isinstance(hash_str, str)
    assert len(hash_str) <= TEST_MAX_LEN
