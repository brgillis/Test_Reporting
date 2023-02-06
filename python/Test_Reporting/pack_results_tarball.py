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

import json
import logging
import os
from argparse import ArgumentParser
from copy import deepcopy
from logging import getLogger
from typing import List, TYPE_CHECKING

from Test_Reporting.utility.constants import JSON_EXT, TARBALL_EXT, XML_EXT
from Test_Reporting.utility.misc import (get_qualified_path, get_relative_path, is_valid_json_filename,
                                         is_valid_xml_filename,
                                         log_entry_exit, tar_files, )
from Test_Reporting.utility.product_parsing import parse_xml_product

if TYPE_CHECKING:
    import Namespace  # noqa F401

logger = getLogger(__name__)


@log_entry_exit(logger)
def get_pack_argument_parser():
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

    parser = get_pack_argument_parser()

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

    # Work with a deepcopy of `args` to avoid surprise from modifying it
    args = deepcopy(args)

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

    target_relpath = get_relative_path(args.target, args.workdir)
    l_files_to_pack: List[str]
    if target_is_xml:
        l_files_to_pack = get_l_files_to_pack_from_product(product_filename=target_relpath,
                                                           workdir=args.workdir)
    else:
        l_files_to_pack = get_l_files_to_pack_from_listfile(listfile_filename=target_relpath,
                                                            workdir=args.workdir)

    logger.debug("Packing files: %s", l_files_to_pack)

    # Check for any missing files and exclude them from the list
    l_existing_files_to_pack = [f for f in l_files_to_pack if os.path.isfile(os.path.join(args.workdir, f))]

    # Warn for any missing files
    if len(l_existing_files_to_pack) < len(l_files_to_pack):
        s_existing_files_to_pack = set(l_existing_files_to_pack)
        logger.warning("%i files were referenced but could not be found. These files were: %s",
                       len(l_files_to_pack) - len(l_existing_files_to_pack),
                       [f for f in l_files_to_pack if f not in s_existing_files_to_pack])

    tar_files(tarball_filename=args.output,
              l_filenames=l_existing_files_to_pack,
              workdir=args.workdir,
              delete_files=False)


@log_entry_exit(logger)
def get_l_files_to_pack_from_listfile(listfile_filename, workdir):
    """Parses a `.json` listfile and the files it points to, getting a list of all these files so that they can be
    packed into a tarball.

    Parameters
    ----------
    listfile_filename : str
        The `.json` listfile filename relative to `workdir`.
    workdir : str
        The work directory in which all files are stored.

    Returns
    -------
    l_files_to_pack : List[str]
        List of filenames of files to be packed, relative to `workdir`.
    """

    # Read in the listfile
    qualified_listfile_filename = os.path.join(workdir, listfile_filename)
    with open(qualified_listfile_filename, "r") as fi:
        l_product_filenames = json.load(fi)

    # Combine the files for each product this listfile points to
    l_files_to_pack = [listfile_filename]
    for product_filename in l_product_filenames:
        l_files_to_pack += get_l_files_to_pack_from_product(product_filename=product_filename,
                                                            workdir=workdir)

    return l_files_to_pack


@log_entry_exit(logger)
def get_l_files_to_pack_from_product(product_filename, workdir):
    """Parses a `.xml` data product and the files it points to, getting a list of all these files so that they can be
    packed into a tarball.

    Parameters
    ----------
    product_filename : str
        The `.xml` product filename relative to `workdir`.
    workdir : str
        The work directory in which all files are stored.

    Returns
    -------
    l_files_to_pack : List[str]
        List of filenames of files to be packed, relative to `workdir`.
    """

    # Start off by including this product's filename in the output list
    l_files_to_pack = [product_filename]

    # Read the product into memory, then get all filenames from it
    product = parse_xml_product(os.path.join(workdir, product_filename))
    l_files_to_pack += [tr.analysis_result.textfiles_tarball for tr in product.l_test_results]
    l_files_to_pack += [tr.analysis_result.figures_tarball for tr in product.l_test_results]

    return l_files_to_pack


if __name__ == "__main__":

    main()
