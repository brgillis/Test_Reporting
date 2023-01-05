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
    test_name = "Shear-Bias"

    @staticmethod
    def _get_d_figure_filenames(l_figure_labels_and_filenames):
        """Parses the figure labels and filenames from a directory and returns a dict appropriately sorting them.
        This may be overridden by child classes if necessary.
        """

        d_figure_filenames = {}

        for (figure_label, figure_filename) in l_figure_labels_and_filenames:

            bin_index = int(figure_label.split("-")[-2])

            if bin_index not in d_figure_filenames:
                d_figure_filenames[bin_index] = {}

            component_index = int(figure_label[-1])

            d_figure_filenames[bin_index][component_index] = figure_filename

        return d_figure_filenames
