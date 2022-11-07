#!/usr/bin/env python

"""
:file: build_all_report_pages.py

:date: 10/11/2022
:author: Bryan Gillis

This python script is run to construct report pages for all validation tests. It reads in the file manifest, and then
calls appropriate functions to construct pages for each test results xml file. This script is called automatically as
part of the continuous-integration pipeline to build report pages.
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
import logging
import os
from argparse import ArgumentParser
from logging import getLogger
from typing import Dict, List, TYPE_CHECKING

from implementations import DEFAULT_BUILD_CALLABLE, D_BUILD_CALLABLES
from utility.constants import MANIFEST_FILENAME, TEST_REPORT_SUMMARY_FILENAME
from utility.misc import log_entry_exit
from utility.test_report_summary import build_test_report_summary, update_summary
from utility.test_writing import TestMeta

if TYPE_CHECKING:
    import Namespace  # noqa F401

logger = getLogger(__name__)


@log_entry_exit(logger)
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
                             f"tarballs to have results pages built. Default: {MANIFEST_FILENAME}")
    parser.add_argument("--rootdir", type=str, default=os.getcwd(),
                        help="The root directory of this project, or a copied instance thereof. Default: (Current "
                             "directory)")
    parser.add_argument("--log-level", type=str, default="INFO",
                        help="The desired level to log at. Allowed values are: 'DEBUG', 'INFO', 'WARNING', 'ERROR, "
                             "'CRITICAL'. Default: 'INFO'")

    return parser


@log_entry_exit(logger)
def parse_args():
    """Parses arguments for this executable.

    Returns
    -------
    args : Namespace
        The parsed arguments.
    """

    parser = get_build_argument_parser()

    args = parser.parse_args()

    return args


@log_entry_exit(logger)
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

    with open(qualified_manifest_filename, "r") as fi:
        d_manifest = json.load(fi)

    logger.info(f"Successfully read in file manifest: {d_manifest}")

    return d_manifest


@log_entry_exit(logger)
def main():
    """Standard entry-point function for this script.
    """

    args = parse_args()

    logging.basicConfig(level=args.log_level)

    logger.info("#")
    logger.info(f"# Beginning execution of script `{__file__}`")
    logger.info("#")

    run_build_from_args(args)

    logger.info("#")
    logger.info(f"# Finished execution of script `{__file__}`")
    logger.info("#")


@log_entry_exit(logger)
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

        build_function = D_BUILD_CALLABLES.get(key)

        # Rather than using the default functionality of the dict's `get` method, we check explicitly so we can log
        # in that case
        if not build_function:
            logger.info(f"No build function provided for key '{key}'; using default implementation.")
            build_function = DEFAULT_BUILD_CALLABLE

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
