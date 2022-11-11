"""
:file: specialization_keys.py

:date: 11/04/2022
:author: Bryan Gillis

This python module defines implementations of building test reports for specific validation tests and for the default
case where no specific implementation is defined.

Instructions
------------

To define a new implementation, the following is the recommended procedure:

1. Choose a unique primary key (a lower-case string). This will be used in the manifest file to indicate the file for
   which this implementation should be used. This should be defined as a constant in the "Primary keys" section of this
   file, to allow easy changing of it in one place if desired in the future.

2. If there are multiple variants of this implementation, choose unique secondary keys for each of these and
   similarly define them as constants in a new "Secondary keys" section.

3. Define an implementation and import it to this file. This can most easily be an instance of the
   `ReportSummaryWriter` class or a child of it, but can also be any callable which share's the signature of its
   `__call__` method if desired. If using the `ReportSummaryWriter` class, see its documentation for instructions on
   how
   do define a new implementation.

4. In the definition of the `D_BUILD_CALLABLES` dict in this module, add an entry with the chosen primary key and
   implementation.

5. Add appropriate unit tests of all added functionality, including extending existing tests as appropriate.
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

from specializations.cti_gal import CtiGalReportSummaryWriter
from utility.report_writing import BUILD_CALLABLE_TYPE, ReportSummaryWriter

# Primary keys
CTI_GAL_KEY = "cti_gal"

# Secondary keys for the CTI-Gal test case
OBS_KEY = "obs"
EXP_KEY = "exp"

# The build functions assigned to each key. The function assigned to the `None` key will be used if a key is used
# in the manifest which doesn't have a specific build function defined here
D_BUILD_CALLABLES: Dict[Optional[str], BUILD_CALLABLE_TYPE] = {CTI_GAL_KEY: CtiGalReportSummaryWriter(), }

DEFAULT_BUILD_CALLABLE = ReportSummaryWriter()
