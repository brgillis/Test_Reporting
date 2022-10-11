#!/usr/bin/env python

"""
:file: build_all_report_pages.py

:date: 10/11/2022
:author: Bryan Gillis

This python script is run to construct report pages for all validation tests. It reads in the file manifest, and then
calls appropriate functions to construct pages for each test results xml file.
"""
import json
import os
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

from argparse import ArgumentParser
from logging import getLogger
from typing import Dict

MANIFEST_FILENAME = "manifest.json"
DATA_DIR = "data"

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

    logger.debug("Exiting `main`.")


if __name__ == "__main__":
    main()
