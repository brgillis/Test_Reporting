"""
:file: product_parsing_test.py

:date: 10/14/2022
:author: Bryan Gillis

Unit tests of parsing XML files.
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
from datetime import datetime

from testing.common import TEST_XML_FILENAME
from utility.constants import TEST_DATA_DIR
from utility.product_parsing import RequirementResults, SingleTestResult, SupplementaryInfo, parse_xml_product


def test_parse_xml_product(rootdir):
    """Unit test of the `parse_xml_file` method.

    Parameters
    ----------
    rootdir : str
        Fixture which provides the root directory of the project
    """

    qualified_xml_filename = os.path.join(rootdir, TEST_DATA_DIR, TEST_XML_FILENAME)

    test_results = parse_xml_product(qualified_xml_filename)

    # We'll check a few random bits of the product are set up correctly, including those most likely to have failed

    # Check the creation date
    assert (isinstance(test_results.creation_date, datetime))
    assert test_results.creation_date.year == 2021
    assert test_results.creation_date.second == 43

    # Check the test results list
    assert len(test_results.l_test_results) == 24
    test_results_0 = test_results.l_test_results[0]
    assert isinstance(test_results_0, SingleTestResult)
    assert test_results_0.test_id == "T-SHE-000010-CTI-gal-GLOBAL-KSB"

    # Check the Requirements list
    assert len(test_results_0.l_requirements) == 1
    requirement_0 = test_results_0.l_requirements[0]
    assert isinstance(requirement_0, RequirementResults)
    assert requirement_0.req_id == "R-SHE-CAL-F-140"

    # Check the SupplementaryInfo
    assert len(requirement_0.l_supp_info) == 2
    info_1 = requirement_0.l_supp_info[1]
    assert isinstance(info_1, SupplementaryInfo)
    assert info_1.info_key == "INTERCEPT_INFO"

    # Check the filenames
    assert (test_results_0.analysis_result.figures_tarball ==
            "data/EUC_SHE_CTI-GAL-ANALYSIS-FILES_FIGURES-7814-_20211203T112445.695596Z_08.02.tar.gz")
    assert (test_results_0.analysis_result.textfiles_tarball ==
            "data/EUC_SHE_CTI-GAL-ANALYSIS-FILES_TEXTFILES-7814-_20211203T112445.653709Z_08.02.tar.gz")
