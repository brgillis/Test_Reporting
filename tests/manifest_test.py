"""
:file: manifest_test.py

:date: 10/11/2022
:author: Bryan Gillis

Unit tests of reading in .json manifest files.
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

import json
import os

import pytest

from build_all_report_pages import read_manifest
from utility.constants import (CTI_GAL_KEY, EXP_KEY, MANIFEST_FILENAME, OBS_KEY, S_MANIFEST_PRIMARY_KEYS,
                               S_MANIFEST_SECONDARY_KEYS, TESTS_DIR, )

MOCK_MANIFEST_FILENAME = "mock_manifest.json"
MOCK_CTI_GAL_OBS_FILENAME = "she_obs_cti_gal.tar.gz"

D_MOCK_MANIFEST = {
    CTI_GAL_KEY: {
        OBS_KEY: "she_obs_cti_gal.tar.gz",
        EXP_KEY: None
        }
    }


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


def test_provided_manifest(rootdir):
    """Unit test that the provided manifest file in this repo can be read in and provides sensible values.

    Parameters
    ----------
    rootdir : str
        Fixture (defined above) which provides the root directory of the project.
    """

    qualified_manifest_filename = os.path.join(rootdir, MANIFEST_FILENAME)

    d_manifest = read_manifest(qualified_manifest_filename)

    assert isinstance(d_manifest, dict)

    for key, value in d_manifest.items():

        # Check that the primary keys are all recognized
        assert key in S_MANIFEST_PRIMARY_KEYS, f"Unrecognized key in manifest: {key}. Allowed keys are: " \
                                               f"{sorted(S_MANIFEST_PRIMARY_KEYS)}."

        # If the value is a dict, check that all keys are known secondary keys. Otherwise, check that the value is a str
        if isinstance(value, dict):

            # Check that the keys of the dict are all recognise, and the values are all strings
            for subkey, subvalue in value.items():

                assert subkey in S_MANIFEST_SECONDARY_KEYS, f"Unrecognized subkey in manifest: {key}. Allowed " \
                                                            f"subkeys are: {sorted(S_MANIFEST_PRIMARY_KEYS)}."

                assert (isinstance(subvalue, str) or
                        subvalue is None), f"Invalid subvalue in manifest: {subvalue}, with type " \
                                           f"{type(subvalue)}. All subvalues must be strings or null."

        elif value is not None:

            assert isinstance(value, str), f"Invalid value in manifest: {value}, with type {type(value)}. All values " \
                                           f"must be either strings, dicts, or null."
