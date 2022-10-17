"""
:file: utility/constants.py

:date: 10/12/2022
:author: Bryan Gillis

This python module defines constants used throughout this project.
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

# Filenames and directories. All are relative to the root of the project

# Files and directories which already exist in the project
MANIFEST_FILENAME = "manifest.json"

AUX_DIR = "auxdir"
TEST_REPORT_TEMPLATE_FILENAME = "Test_Reports_template.md"

DATA_DIR = "data"

PYTHON_DIR = "python"

PUBLIC_DIR = "public"
IMAGES_SUBDIR = "images"
TEST_REPORTS_SUBDIR = "TR"
SUMMARY_FILENAME = "SUMMARY.md"

TESTS_DIR = "tests"
TEST_DATA_DIR = "test_data"

# Temporary work directory
WORKDIR = "workdir"

# Desired filenames and directories to use for created markdown files to report test results
TEST_REPORT_SUMMARY_FILENAME = "Test_Reports.md"
REPORT_SUBDIR = "reports"

# Primary keys within the manifest JSON file
CTI_GAL_KEY = "cti_gal"

S_MANIFEST_PRIMARY_KEYS = {CTI_GAL_KEY,
                           }

# Secondary keys within the manifest JSON file
OBS_KEY = "obs"
EXP_KEY = "exp"

S_MANIFEST_SECONDARY_KEYS = {OBS_KEY,
                             EXP_KEY,
                             }
