#!/usr/bin/env python

"""
:file: Test_Reporting/build_report.py

:date: 10/11/2022
:author: Bryan Gillis

This python script is run to construct report pages for a single provided validation test. It may be provided with
either a tarball of the results and associated data or the filename of a results data product. By default,
it builds the report in the current directory, but this can be modified through command-line arguments.
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

import logging
import os
from argparse import ArgumentParser
from logging import getLogger
from typing import TYPE_CHECKING

from Test_Reporting.specialization_keys import DEFAULT_BUILD_CALLABLE, D_BUILD_CALLABLES
from Test_Reporting.utility.misc import get_qualified_path, log_entry_exit

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

    parser.add_argument("target", type=str,
                        help="The filename of either a tarball (\"*.tar\" or \"*.tar.gz\") of test results or a "
                             "results data product (\"*.xml\"), for which reports should be build. If the latter is "
                             "provided, data files it points to will be assumed to be in the 'data' directory "
                             "relative to it unless otherwise specified with the \"--datadir\" argument.")
    parser.add_argument("--key", type=str, default=None,
                        help="The key corresponding to the type of the results product, which can be used to invoke a "
                             "specialized builder for it. Default: None (will be build using the default builder).")
    parser.add_argument("--datadir", type=str, default=None,
                        help="If the target is a results data product, this can be used to specify the directory that "
                             "all data files it points to are relative to (this would be the \"workdir\" of the "
                             "program which generated it). Default: (Directory containing `target`)")
    parser.add_argument("--reportdir", type=str, default=os.getcwd(),
                        help="The directory in which to build the report pages. Default: (Current directory).")
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


def main():
    """Standard entry-point function for this script.
    """

    args = parse_args()

    logging.basicConfig(level=args.log_level)

    logger.info("#")
    logger.info("# Beginning execution of script `%s`", __file__)
    logger.info("#")

    run_build_from_args(args)

    logger.info("#")
    logger.info("# Finished execution of script `%s`", __file__)
    logger.info("#")


@log_entry_exit(logger)
def run_build_from_args(args):
    """Workhorse function to perform primary execution of this script, using the provided parsed arguments.

    Parameters
    ----------
    args : Namespace
        The parsed arguments for this script.
    """

    # Make sure all arguments give absolute paths
    args.target = get_qualified_path(args.target)
    if args.datadir is not None:
        args.datadir = get_qualified_path(args.datadir)
    args.reportdir = get_qualified_path(args.reportdir)

    build_callable = D_BUILD_CALLABLES.get(args.key)

    # Rather than using the default functionality of the dict's `get` method, we check explicitly, so we can log
    # in that case
    if not build_callable:
        logger.info("No build callable provided for key '%s'; using default implementation "
                    "%s to construct test report from data: %s.", args.key, DEFAULT_BUILD_CALLABLE, args.target)
        build_callable = DEFAULT_BUILD_CALLABLE
    else:
        logger.info("Using build callable %s to construct test report from data: %s.", build_callable, args.target)

    build_callable(args.target, os.path.split(args.target)[0], args.reportdir, args.datadir)


if __name__ == "__main__":

    main()
