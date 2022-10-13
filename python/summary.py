"""
:file: summary.py

:date: 10/13/2022
:author: Bryan Gillis

Functions to handle updating the SUMMARY.md file.
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

from utility.constants import PUBLIC_DIR, SUMMARY_FILENAME


def update_summary(test_report_summary_filename,
                   l_test_and_file_names,
                   rootdir):
    """Builds a markdown file containing the summary of the Test Reports section at the desired location, containing a
    table linking to the individual pages.

    Parameters
    ----------
    test_report_summary_filename : str
        The filename of the Markdown (.md) file containing the summary of the Test Reports section
    l_test_and_file_names : List[Tuple[str,str]]
        A list of tuples, each containing a string for the name of a test in the first element and the name of the
        markdown file (relative to the reports directory) in the second element.
    rootdir: str
        The root directory of this project (or during unit testing, a copied instance of this project).
    """

    qualified_summary_filename = os.path.join(rootdir, PUBLIC_DIR, SUMMARY_FILENAME)

    # Open the summary file to append to it
    with open(qualified_summary_filename, 'a') as fo:

        # Add a line for the summary page
        fo.write(f"* [Test Reports]({test_report_summary_filename})\n")

        # Add a line for each test
        for test_name, md_filename in l_test_and_file_names:

            if not md_filename.endswith('.md'):
                raise ValueError("Filenames of test reports passed to `update_summary` must end with '.md'.")

            fo.write(f"  * [{test_name}]({md_filename})\n")
