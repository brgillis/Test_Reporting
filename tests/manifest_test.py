"""
:file: manifest_test.py

:date: 10/11/2022
:author: Bryan Gillis

Unit tests of reading in .json manifest files.
"""
import json
import os

import pytest

from build_all_report_pages import D_BUILD_FUNCTIONS, read_manifest
from utility.constants import CTI_GAL_KEY, EXP_KEY, MANIFEST_FILENAME, OBS_KEY

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

MOCK_MANIFEST_FILENAME = "mock_manifest.json"
MOCK_CTI_GAL_OBS_FILENAME = "she_obs_cti_gal.tar.gz"

D_MOCK_MANIFEST = {
    CTI_GAL_KEY: {
        OBS_KEY: "she_obs_cti_gal.tar.gz",
        EXP_KEY: None
        }
    }


def make_mock_manifest(qualified_manifest_filename):
    """Creates a mock manifest file, saving it to the provided location.

    Parameters
    ----------
    qualified_manifest_filename : str
        Desired fully-qualified filename for the manifest file to be created.
    """

    with open(qualified_manifest_filename, "w") as fo:
        json.dump(D_MOCK_MANIFEST, fo)


@pytest.fixture
def mock_manifest(tmpdir):
    """A fixture to provide the filename of a mock manifest file which can be used for testing.

    Parameters
    ----------
    tmpdir : local
        pytest's `tmpdir` fixture

    Returns
    -------
    mock_manifest : str
        The fully-qualified filename of the mock manifest file.

    """

    qualified_manifest_filename = os.path.join(tmpdir, MOCK_MANIFEST_FILENAME)

    # Create the mock manifest only if it doesn't already exist
    if not os.path.exists(qualified_manifest_filename):
        make_mock_manifest(qualified_manifest_filename)

    return qualified_manifest_filename


def test_mock_manifest(mock_manifest):
    """Unit test that a mock manifest can be read in, providing the expected values.

    Parameters
    ----------
    mock_manifest : str
        Fixture (defined above) which creates a mock manifest files and provides the fully-qualified filename of it
    """

    d_manifest = read_manifest(mock_manifest)

    # Check that the manifest was read in as expected
    assert isinstance(d_manifest, dict)

    d_cti_gal = d_manifest[CTI_GAL_KEY]

    assert d_cti_gal[OBS_KEY] == MOCK_CTI_GAL_OBS_FILENAME
    assert d_cti_gal[EXP_KEY] is None


def test_provided_manifest():
    """Unit test that the provided manifest file in this repo can be read in and provides sensible values.
    """

    d_manifest = read_manifest(MANIFEST_FILENAME)

    assert isinstance(d_manifest, dict)

    for key, value in d_manifest.items():
        assert key in D_BUILD_FUNCTIONS
        assert isinstance(value, str) or isinstance(value, dict)
