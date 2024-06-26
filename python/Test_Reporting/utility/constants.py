"""
:file: Test_Reporting/utility/constants.py

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

DATA_DIR = "data"

PYTHON_DIR = "python"

PUBLIC_DIR = "public"
IMAGES_SUBDIR = "images"
README_FILENAME = "README.md"
SUMMARY_FILENAME = "SUMMARY.md"

TESTS_DIR = "tests"
TEST_DATA_DIR = "test_data"

# Desired filenames and directories to use for created markdown files to report test results
TEST_REPORT_SUMMARY_FILENAME = "Test_Reports.md"
TEST_REPORTS_SUBDIR = "TR"

# Heading for a Table of Contents
HEADING_TOC = "## Table of Contents"

# The subdir in which data associated with XML data products is stored
DATA_SUBDIR = "data"

# Filename extensions
XML_EXT = ".xml"
JSON_EXT = ".json"
HTML_EXT = ".html"
MD_EXT = ".md"
TARBALL_EXT = ".tar.gz"

# Strings expected in test results products
STR_PASS = "PASSED"
STR_FAIL = "FAILED"
