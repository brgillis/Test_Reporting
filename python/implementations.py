"""
:file: implementations.py

:date: 11/04/2022
:author: Bryan Gillis

This python module defines implementations of building test reports for specific validation tests and for the default
case where no specific implementation is defined. These are generally expected to be an instance of the
`TestSummaryWriter` class or a child of it, but can be any callable with the same signature as that class's
`__call__` method which performs the desired functionality if this class is not suitable.
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

from typing import Dict, Optional

from utility.test_writing import BUILD_FUNCTION_TYPE, TestSummaryWriter

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

# The build functions assigned to each key. The function assigned to the `None` key will be used if a key is used
# in the manifest which doesn't have a specific build function defined here
D_BUILD_FUNCTIONS: Dict[Optional[str], BUILD_FUNCTION_TYPE] = {CTI_GAL_KEY: TestSummaryWriter(test_name="CTI-Gal"),
                                                               None: TestSummaryWriter()}
