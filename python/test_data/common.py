"""
:file: common.py

:date: 10/18/2022
:author: Bryan Gillis

Common code for unit tests in this project.
"""
from utility.test_writing import NameAndFileName, SummaryWriteOutput

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

TEST_TARBALL_FILENAME = "she_obs_cti_gal.tar.gz"
TEST_XML_FILENAME = "she_observation_cti_gal_validation_test_results_product.xml"
L_SUMMARY_WRITE_OUTPUT = [SummaryWriteOutput(NameAndFileName("T1", "T1.md"), [NameAndFileName("TC1-1", "TC1-1.md")]),
                          SummaryWriteOutput(NameAndFileName("T2", "T2a.md"), [NameAndFileName("TC2-1", "TC2-1.md"),
                                                                               NameAndFileName("TC2-2", "TC2-2.md")])]
