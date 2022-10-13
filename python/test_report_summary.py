"""
:file: test_report_summary.py

:date: 10/13/2022
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

import os

from utility.constants import AUX_DIR, PUBLIC_DIR, TEST_REPORT_TEMPLATE_FILENAME


def build_test_report_summary(test_report_summary_filename,
                              l_test_and_file_names,
                              rootdir):
    """Builds a markdown file containing the summary of the Test Reports section at the desired location, containing a
    table linking to the individual pages.

    Parameters
    ----------
    test_report_summary_filename : str
        The desired filename of the Markdown (.md) file to be created, containing the summary of the Test Reports
        section
    l_test_and_file_names : List[Tuple[str,str]]
        A list of tuples, each containing a string for the name of a test in the first element and the name of the
        markdown file (relative to the reports directory) in the second element.
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
        for test_name, md_filename in l_test_and_file_names:

            if not md_filename.endswith('.md'):
                raise ValueError("Filenames of test reports passed to `build_test_report_summary` must end with '.md'.")
            html_filename = f"{md_filename[:-3]}.html"

            test_line = f"|[{test_name}]({html_filename})|\n"
            fo.write(test_line)
