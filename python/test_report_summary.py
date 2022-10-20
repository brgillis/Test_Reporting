"""
:file: test_report_summary.py

:date: 10/13/2022
:author: Bryan Gillis

Functions to handle building a new test report summary file.
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
from typing import TYPE_CHECKING

from utility.constants import AUX_DIR, PUBLIC_DIR, TEST_REPORT_TEMPLATE_FILENAME

if TYPE_CHECKING:
    from typing import Sequence  # noqa F401
    from utility.test_writing import TestMeta  # noqa F401


def build_test_report_summary(test_report_summary_filename,
                              l_test_meta,
                              rootdir):
    """Builds a markdown file containing the summary of the Test Reports section at the desired location, containing a
    table linking to the individual pages.

    Parameters
    ----------
    test_report_summary_filename : str
        The desired filename of the Markdown (.md) file to be created, containing the summary of the Test Reports
        section
    l_test_meta : Sequence[TestMeta]
        A list of objects, each containing the test name and filename, and a list of test case names and filenames
    rootdir: str
        The root directory of this project (or during unit testing, a copied instance of this project).
    """

    qualified_test_report_summary_filename = os.path.join(rootdir, PUBLIC_DIR, test_report_summary_filename)
    qualified_test_report_template_filename = os.path.join(rootdir, AUX_DIR, TEST_REPORT_TEMPLATE_FILENAME)

    # Open the file we want to write
    with open(qualified_test_report_summary_filename, 'w') as fo:

        # First, copy all lines from the template file
        with open(qualified_test_report_template_filename, 'r') as fi:
            for line in fi:
                fo.write(line)

        # Now, add a line for each test
        for test_meta in l_test_meta:

            if not test_meta.filename.endswith('.md'):
                raise ValueError("Filenames of test reports passed to `build_test_report_summary` must end with '.md'.")
            test_html_filename = f"{test_meta.filename[:-3]}.html"

            test_line = f"|[{test_meta.name}]({test_html_filename})|{test_meta.num_passed}|{test_meta.num_failed}|\n"
            fo.write(test_line)
