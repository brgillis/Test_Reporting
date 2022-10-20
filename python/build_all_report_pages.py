#!/usr/bin/env python

"""
:file: build_all_report_pages.py

:date: 10/11/2022
:author: Bryan Gillis

This python script is run to construct report pages for all validation tests. It reads in the file manifest, and then
calls appropriate functions to construct pages for each test results xml file.
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
from argparse import ArgumentParser
from logging import getLogger
from typing import Dict, List, TYPE_CHECKING

from test_report_summary import build_test_report_summary, update_summary
from utility.constants import CTI_GAL_KEY, MANIFEST_FILENAME, TEST_REPORT_SUMMARY_FILENAME
from utility.test_writing import BUILD_FUNCTION_TYPE, TestMeta, TestSummaryWriter

if TYPE_CHECKING:
    import Namespace  # noqa F401

D_BUILD_FUNCTIONS: Dict[str, BUILD_FUNCTION_TYPE] = {CTI_GAL_KEY: TestSummaryWriter()}

logger = getLogger(__name__)


def get_build_argument_parser():
    """Get an argument parser for this script.

    Returns
    -------
    parser : ArgumentParser
        An argument parser set up with the allowed command-line arguments for this script.
    """

    parser = ArgumentParser()
    parser.add_argument("--manifest", type=str, default=MANIFEST_FILENAME,
                        help="The name of the .json-format file manifest, containing the validation test results "
                             "tarballs to have results pages built.")
    parser.add_argument("--rootdir", type=str, default=None,
                        help="The root directory of this project, or a copied instance thereof. Will default to the "
                             "current directory if not provided.")
    return parser


def parse_args():
    """Parses arguments for this executable.

    Returns
    -------
    args : Namespace
        The parsed arguments
    """

    parser = get_build_argument_parser()

    args = parser.parse_args()

    if args.rootdir is None:
        args.rootdir = os.getcwd()

    return args


def read_manifest(qualified_manifest_filename):
    """Read in the .json-format manifest file.

    Parameters
    ----------
    qualified_manifest_filename : str
        The fully-qualified filename of the .json-format manifest file

    Returns
    -------
    d_manifest : Dict[str, str or Dict[str, str or None] or None]
        The file manifest, stored as a dict
    """

    logger.debug("Entering `read_manifest`.")

    with open(qualified_manifest_filename, "r") as fi:
        d_manifest = json.load(fi)

    logger.info(f"Successfully read in file manifest: {d_manifest}")

    logger.debug("Exiting `read_manifest`.")

    return d_manifest


def main():
    """Standard entry-point function for this script.
    """

    logger.debug("Entering `main`.")

    args = parse_args()

    run_build_from_args(args)

    logger.debug("Exiting `main`.")


def run_build_from_args(args):
    """Workhorse function to perform primary execution of this script, using the provided parsed arguments.

    Parameters
    ----------
    args : Namespace
        The parsed arguments for this script
    """

    d_manifest = read_manifest(os.path.join(args.rootdir, args.manifest))

    l_test_meta: List[TestMeta] = []

    # Call the build function for each file in the manifest
    for key, value in d_manifest.items():

        build_function = D_BUILD_FUNCTIONS.get(key)

        if not build_function:
            logger.debug(f"No build function provided for key '{key}'")
            continue

        l_test_meta += build_function(value, args.rootdir)

    # Build the summary page for test reports
    build_test_report_summary(test_report_summary_filename=TEST_REPORT_SUMMARY_FILENAME,
                              l_test_meta=l_test_meta,
                              rootdir=args.rootdir)

    # Update the public SUMMARY.md file with new files created
    update_summary(test_report_summary_filename=TEST_REPORT_SUMMARY_FILENAME,
                   l_test_meta=l_test_meta,
                   rootdir=args.rootdir)


if __name__ == "__main__":
    main()
