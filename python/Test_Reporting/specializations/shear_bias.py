"""
:file: Test_Reporting/specializations/shear_bias.py

:date: 01/05/2023
:author: Bryan Gillis

Module providing a specialized ReportSummaryWriter for Shear Bias test cases.
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

from dataclasses import dataclass
from logging import getLogger

from Test_Reporting.specializations.binned import BinnedReportSummaryWriter

logger = getLogger(__name__)


class ShearBiasReportSummaryWriter(BinnedReportSummaryWriter):
    test_name = "Shear Bias"
