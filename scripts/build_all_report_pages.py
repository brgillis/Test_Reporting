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
from typing import Callable, Dict, Optional, Union

MANIFEST_FILENAME = "manifest.json"
DATA_DIR = "data"
CTI_GAL_KEY = "cti_gal"
OBS_KEY = "obs"
EXP_KEY = "exp"

BUILD_FUNCTION_TYPE = Optional[Callable[[Union[str, Dict[str, str]]], None]]
D_BUILD_FUNCTIONS: Dict[str, BUILD_FUNCTION_TYPE] = {CTI_GAL_KEY: None}

logger = getLogger(__name__)


def parse_args():
    """Parses arguments for this executable.

    Returns
    -------
    args : Namespace
        The parsed arguments
    """

    logger.debug("Entering `parse_args`.")

    parser = ArgumentParser()

    parser.add_argument("--manifest", type=str, default=MANIFEST_FILENAME)

    args = parser.parse_args()

    logger.debug("Exiting `parse_args`.")

    return args


def read_manifest(qualified_manifest_filename):
    """

    Parameters
    ----------
    qualified_manifest_filename : str
        The fully-qualified filename of the .json-format manifest file

    Returns
    -------
    d_manifest : Dict[str, str or Dict[str,str]]
        The file manifest, stored as a

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

    workdir = os.getcwd()

    d_manifest = read_manifest(os.path.join(workdir, args.manifest))

    # Call the build function for each file in the manifest
    for key, value in d_manifest.items():

        build_function = D_BUILD_FUNCTIONS.get(key)

        if not build_function:
            logger.debug(f"No build function provided for key {key}")
            continue

        build_function(value)

    logger.debug("Exiting `main`.")


if __name__ == "__main__":
    main()
