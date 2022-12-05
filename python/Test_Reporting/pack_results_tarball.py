#!/usr/bin/env python

"""
:file: Test_Reporting/pack_results_tarball.py

:date: 12/05/2022
:author: Bryan Gillis

This python script is run to collect a validation test results product (or listfile thereof) and all its associated
datafiles into a tarball which can be easily moved into this project for publishing.
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
from typing import List, TYPE_CHECKING

from Test_Reporting.specialization_keys import DEFAULT_BUILD_CALLABLE, D_BUILD_CALLABLES
from Test_Reporting.utility.constants import JSON_EXT, TARBALL_EXT, XML_EXT
from Test_Reporting.utility.misc import (get_qualified_path, get_relative_path, is_valid_json_filename,
                                         is_valid_xml_filename,
                                         log_entry_exit, tar_files, )

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
                        help=f"The filename of either a `{XML_EXT}` validation test results data product or a `"
                             f"{JSON_EXT}` listfile of multiple such products. All products pointed to this way, "
                             f"plus all datafiles they point to, will be packed into a `{TARBALL_EXT}` tarball.")
    parser.add_argument("--workdir", type=str, default=None,
                        help=f"The work directory where all files pointed to by either a target `{JSON_EXT}` listfile "
                             f"or any `{XML_EXT}` data products are relative to. Default: (Directory containing "
                             "`target`)")
    parser.add_argument("--output", type=str, default=None,
                        help="The desired filename of the tarball to be created. Default: (`target`, with extension "
                             f"replaced with \"{TARBALL_EXT}\".")
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

    run_pack_from_args(args)

    logger.info("#")
    logger.info("# Finished execution of script `%s`", __file__)
    logger.info("#")


@log_entry_exit(logger)
def run_pack_from_args(args):
    """Workhorse function to perform primary execution of this script, using the provided parsed arguments.

    Parameters
    ----------
    args : Namespace
        The parsed arguments for this script.
    """

    # Determine input, making sure all use fully-qualified paths

    args.target = get_qualified_path(args.target)

    target_is_xml = is_valid_xml_filename(args.target)
    target_is_json = is_valid_json_filename(args.target)

    if not (target_is_xml ^ target_is_json):
        raise ValueError(f"Command-line argument `target` must point to a valid `{XML_EXT}` or `{JSON_EXT}` file.")

    if args.workdir is not None:
        args.workdir = get_qualified_path(args.workdir)
    else:
        args.workdir = os.path.split(args.target)[0]

    if args.output is not None:
        args.output = get_relative_path(args.output, args.workdir)
    elif target_is_xml:
        args.output = f"{args.target[:-len(XML_EXT)]}{TARBALL_EXT}"
    else:
        args.output = f"{args.target[:-len(JSON_EXT)]}{TARBALL_EXT}"

    # Get a list of all files to pack into the tarball by reading the product/listfile

    target_relpath = get_relative_path(args.target)
    l_files_to_pack: List[str]
    if target_is_xml:
        l_files_to_pack = get_l_files_to_pack_from_product(product_filename=target_relpath,
                                                           workdir=args.workdir)
    else:
        l_files_to_pack = get_l_files_to_pack_from_listfile(listfile_filename=target_relpath,
                                                            workdir=args.workdir)

    logger.debug("Packing files: %s", l_files_to_pack)

    logger.info("Packing tarball %s", args.output)

    tar_files(tarball_filename=args.output,
              l_filenames=l_files_to_pack,
              workdir=args.workdir,
              delete_files=False)

if __name__ == "__main__":

    main()
