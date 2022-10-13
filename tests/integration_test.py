"""
:file: integration_test.py

:date: 10/13/2022
:author: Bryan Gillis

Unit tests of running the whole script in a minimal state.
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

import build_all_report_pages
from .testing_utility import project_copy  # noqa F401


def test_integration(project_copy):
    """Tests a slimmed-down full execution of the build script.

    Parameters
    ----------
    project_copy : str
        Pytest fixture providing the fully-qualified path to a copy of the project created for testing purposes.
    """

    # Set up the mock arguments
    parser = build_all_report_pages.get_build_argument_parser()
    args = parser.parse_args([])
    args.rootdir = project_copy

    # Call the main workhorse function
    build_all_report_pages.run_build_from_args(args)
