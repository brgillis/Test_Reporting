"""
:file: integration_test.py

:date: 10/13/2022
:author: Bryan Gillis

Unit tests of running the whole script in a minimal state.
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

from Test_Reporting.testing.common import TEST_TARBALL_FILENAME

from Test_Reporting.specialization_keys import CTI_GAL_KEY

from Test_Reporting import build_all_report_pages, build_report
from Test_Reporting.utility.constants import DATA_DIR, PUBLIC_DIR, TEST_REPORT_SUMMARY_FILENAME


def test_build_all_integration(project_copy, test_manifest):
    """Tests a slimmed-down full execution of the build_all script, using the default implementation.

    Parameters
    ----------
    project_copy : str
        Pytest fixture providing the fully-qualified path to a copy of the project created for testing purposes.
    test_manifest : str
        Pytest fixture providing the fully-qualified path to the manifest used for testing the default builder
    """

    # Set up the mock arguments
    parser = build_all_report_pages.get_build_argument_parser()
    args = parser.parse_args([])
    args.rootdir = project_copy
    args.manifest = test_manifest

    # Call the main workhorse function
    build_all_report_pages.run_build_all_from_args(args)

    # Check that output looks as expected

    qualified_test_report_summary_filename = os.path.join(project_copy, PUBLIC_DIR, TEST_REPORT_SUMMARY_FILENAME)
    assert os.path.isfile(qualified_test_report_summary_filename)


def test_cti_gal_integration(project_copy, cti_gal_manifest):
    """Tests a slimmed-down full execution of the build script, using the CTI-Gal specialization.

    Parameters
    ----------
    project_copy : str
    cti_gal_manifest : str
        Pytest fixture providing the fully-qualified path to the manifest used for testing the CTI-Gal builder
    """

    # Set up the mock arguments
    parser = build_all_report_pages.get_build_argument_parser()
    args = parser.parse_args([])
    args.rootdir = project_copy
    args.manifest = cti_gal_manifest

    # Call the main workhorse function
    build_all_report_pages.run_build_all_from_args(args)

    # Check that output looks as expected

    qualified_test_report_summary_filename = os.path.join(project_copy, PUBLIC_DIR, TEST_REPORT_SUMMARY_FILENAME)
    assert os.path.isfile(qualified_test_report_summary_filename)


def test_standalone_integration(project_copy, tmpdir_factory):
    """Tests a full execution of the standalone build script.

    Parameters
    ----------
    project_copy : str
    tmpdir_factory : TempdirFactory
        Pytest fixture providing a factory to create temporary directories for testing.
    """

    # Set up the mock arguments
    parser = build_report.get_build_argument_parser()
    args = parser.parse_args([])
    args.target = os.path.join(project_copy, DATA_DIR, TEST_TARBALL_FILENAME)
    args.datadir = project_copy
    args.reportdir = str(tmpdir_factory.mktemp("project_copy"))
    args.key = CTI_GAL_KEY

    # Call the main workhorse function
    build_report.run_build_from_args(args)

    # Check that output looks as expected

    qualified_test_report_summary_filename = os.path.join(project_copy, PUBLIC_DIR, TEST_REPORT_SUMMARY_FILENAME)
    assert os.path.isfile(qualified_test_report_summary_filename)
