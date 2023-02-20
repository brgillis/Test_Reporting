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
import shutil

from Test_Reporting.specializations.cti_gal import CtiGalReportSummaryWriter

from Test_Reporting.testing.common import TEST_JSON_FILENAME, TEST_TARBALL_FILENAME, TEST_XML_FILENAME

from Test_Reporting.specialization_keys import CTI_GAL_KEY

from Test_Reporting import build_all_report_pages, build_report, pack_results_tarball
from Test_Reporting.utility.constants import DATA_DIR, PUBLIC_DIR, TEST_REPORTS_SUBDIR, TEST_REPORT_SUMMARY_FILENAME

OUTPUT_TARBALL_FILENAME = "output_tarball.tar.gz"


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


def test_standalone_integration_with_tarball(project_copy, tmpdir_factory):
    """Tests a full execution of the standalone build script, targeting a tarball.

    Parameters
    ----------
    project_copy : str
    tmpdir_factory : TempdirFactory
        Pytest fixture providing a factory to create temporary directories for testing.
    """

    # Set up the mock arguments
    parser = build_report.get_build_argument_parser()
    args = parser.parse_args([os.path.join(project_copy, DATA_DIR, TEST_TARBALL_FILENAME)])
    args.reportdir = str(tmpdir_factory.mktemp("reportdir"))
    args.key = CTI_GAL_KEY

    # Call the main workhorse function
    build_report.run_build_from_args(args)

    # Check that output looks as expected

    qualified_test_report_summary_filename = os.path.join(args.reportdir, TEST_REPORTS_SUBDIR,
                                                          f"{CtiGalReportSummaryWriter.test_name}.md")
    assert os.path.isfile(qualified_test_report_summary_filename)


def test_standalone_integration_with_product(project_copy, tmpdir_factory):
    """Tests a full execution of the standalone build script, targeting a data product.

    Parameters
    ----------
    project_copy : str
    tmpdir_factory : TempdirFactory
    """

    mock_datadir = os.path.join(project_copy, "mock_datadir")

    # We'll move the data to a separate directory to test that it can still be found
    shutil.move(os.path.join(project_copy, DATA_DIR, "data/"), mock_datadir)

    # Set up the mock arguments
    parser = build_report.get_build_argument_parser()
    args = parser.parse_args([os.path.join(project_copy, DATA_DIR, TEST_XML_FILENAME)])
    args.datadir = mock_datadir
    args.reportdir = str(tmpdir_factory.mktemp("reportdir"))
    args.key = CTI_GAL_KEY

    # Call the main workhorse function
    build_report.run_build_from_args(args)

    # Check that output looks as expected

    qualified_test_report_summary_filename = os.path.join(args.reportdir, TEST_REPORTS_SUBDIR,
                                                          f"{CtiGalReportSummaryWriter.test_name}.md")
    assert os.path.isfile(qualified_test_report_summary_filename)

    # Also test by leaving args.datadir unspecified

    os.remove(qualified_test_report_summary_filename)
    args.datadir = None
    build_report.run_build_from_args(args)
    assert os.path.isfile(qualified_test_report_summary_filename)


def test_pack_tarball_with_product(project_copy):
    """Tests a full execution of the `pack_results_tarball.py` script, targeting a data product.

    Parameters
    ----------
    project_copy : str
    """

    # Set up the mock arguments
    parser = pack_results_tarball.get_pack_argument_parser()
    args = parser.parse_args([os.path.join(project_copy, DATA_DIR, TEST_XML_FILENAME)])
    args.output = os.path.join(project_copy, OUTPUT_TARBALL_FILENAME)
    args.workdir = project_copy

    # Call the main workhorse function
    pack_results_tarball.run_pack_from_args(args)

    # Check that output looks as expected

    assert os.path.isfile(args.output)


def test_pack_tarball_with_listfile(project_copy):
    """Tests a full execution of the `pack_results_tarball.py` script, targeting a listfile.

    Parameters
    ----------
    project_copy : str
    """

    # Set up the mock arguments
    parser = pack_results_tarball.get_pack_argument_parser()
    args = parser.parse_args([os.path.join(project_copy, DATA_DIR, TEST_JSON_FILENAME)])
    args.output = os.path.join(project_copy, OUTPUT_TARBALL_FILENAME)
    args.workdir = project_copy

    # Call the main workhorse function
    pack_results_tarball.run_pack_from_args(args)

    # Check that output looks as expected

    assert os.path.isfile(args.output)
