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

from utility.constants import TEST_DATA_DIR
from utility.product_parsing import parse_xml_product

TEST_XML_FILENAME = "she_observation_cti_gal_validation_test_results_product.xml"


def test_parse_xml_product(rootdir):
    """Unit test of the `parse_xml_file` method.

    Parameters
    ----------
    rootdir : str
        Fixture which provides the root directory of the project
    """

    qualified_xml_filename = os.path.join(rootdir, TEST_DATA_DIR, TEST_XML_FILENAME)

    test_results = parse_xml_product(qualified_xml_filename)
