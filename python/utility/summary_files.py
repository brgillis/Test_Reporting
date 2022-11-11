"""
:file: utility/summary_files.py

:date: 10/13/2022
:author: Bryan Gillis

Functions to handle building and updating summary files for the test reports that have been generated.
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
from typing import TYPE_CHECKING

from utility.constants import HEADING_TOC, PUBLIC_DIR, README_FILENAME, SUMMARY_FILENAME
from utility.misc import log_entry_exit

if TYPE_CHECKING:
    from typing import Sequence  # noqa F401
    from utility.report_writing import ValTestMeta  # noqa F401

logger = logging.getLogger(__name__)


@log_entry_exit(logger)
def build_test_report_summary(test_report_summary_filename,
                              l_test_meta,
                              rootdir):
    """Builds a markdown file containing the summary of the Test Reports section at the desired location, containing a
    table linking to the individual pages.

    Parameters
    ----------
    test_report_summary_filename : str
        The desired filename of the Markdown (.md) file to be created, containing the summary of the Test Reports
        section.
    l_test_meta : Sequence[ValTestMeta]
        A list of objects, each containing the test name and filename, and a list of test case names and filenames.
    rootdir: str
        The root directory of this project (or during unit testing, a copied instance of this project).
    """

    logger.info("Building test report summary file %s", test_report_summary_filename)

    qualified_test_report_summary_filename = os.path.join(rootdir, PUBLIC_DIR, test_report_summary_filename)

    # Open the file we want to write
    with open(qualified_test_report_summary_filename, 'w') as fo:

        # First, add all the boilerplate lines to the top
        fo.write("# Testing Reports\n\n")
        fo.write("This section contains automatically-generated reports on the validation test results products "
                 "contained in the \"data\" directory of this project. The reports can be found linked in the "
                 "following table:\n\n")
        fo.write("| **Test ID** | **Num Passed** | **Num Failed** |\n")
        fo.write("|:------------|:---------------|:---------------|\n")

        # Now, add a line for each test
        for test_meta in l_test_meta:

            _check_md_filename(test_meta.filename)
            test_html_filename = f"{test_meta.filename[:-3]}.html"

            fo.write(f"| [{test_meta.name}]({test_html_filename}) "
                     f"| {test_meta.num_passed} "
                     f"| {test_meta.num_failed} |\n")

        fo.write("\nThe log file for building these test reports can be found [here](build.log).")


@log_entry_exit(logger)
def update_summary(test_report_summary_filename,
                   l_test_meta,
                   rootdir):
    """Updates the markdown file containing the summary bullet-point-list of files to be compiled in this project.

    Parameters
    ----------
    test_report_summary_filename : str
        The filename of the Markdown (.md) file containing the summary of the Test Reports section.
    l_test_meta : Sequence[ValTestMeta]
    rootdir: str
    """

    qualified_summary_filename = os.path.join(rootdir, PUBLIC_DIR, SUMMARY_FILENAME)

    logger.info("Updating GitBooks SUMMARY.md file: %s", qualified_summary_filename)

    # Open the summary file to append to it
    with open(qualified_summary_filename, 'a') as fo:

        # Add a line for the summary page
        fo.write(f"* [Test Reports]({test_report_summary_filename})\n")

        # Add a line for each test
        for test_meta in l_test_meta:

            fo.write(f"  * [{test_meta.name}]({test_meta.filename})\n")

            # Add a line for each test case, grouped after the associated test
            for test_case_name, test_case_md_filename, passed in test_meta.l_test_case_meta:

                _check_md_filename(test_case_md_filename)

                fo.write(f"    * [{test_case_name}]({test_case_md_filename})\n")


@log_entry_exit(logger)
def update_readme(rootdir):
    """Updates the public README.md file of this project, so it contains a table of contents linking to all files.
    Note that this should only be called after finishing updating the SUMMARY.md file, since it copies from that.

    Parameters
    ----------
    rootdir: str
    """

    qualified_summary_filename = os.path.join(rootdir, PUBLIC_DIR, SUMMARY_FILENAME)
    qualified_readme_filename = os.path.join(rootdir, PUBLIC_DIR, README_FILENAME)

    logger.info("Updating README.md file: %s", qualified_readme_filename)

    # Read in lines from the summary file
    with open(qualified_summary_filename) as fi:
        l_summary_lines = fi.readlines()

    # Open the readme file to append to it a table of contents with all lines from the summary file

    with open(qualified_readme_filename, 'a') as fo:

        fo.write(f"\n{HEADING_TOC}\n\n")

        for line in l_summary_lines:

            # Skip the heading line and empty lines
            if line.startswith("#") or line == "\n":
                continue

            # Copy all other lines
            fo.write(line)


def _check_md_filename(filename):
    """Private method to check that a filename ends with `.md' and raise an exception if not.
    """
    if not filename.endswith('.md'):
        raise ValueError(f"Filename '{filename}' must end with '.md'.")
