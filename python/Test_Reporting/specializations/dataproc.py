"""
:file: Test_Reporting/specializations/dataproc.py

:date: 01/23/2023
:author: Bryan Gillis

Module providing a specialized ReportSummaryWriter for DataProc test.
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

from logging import getLogger

from Test_Reporting.utility.constants import STR_FAIL, STR_PASS
from Test_Reporting.utility.misc import log_entry_exit
from Test_Reporting.utility.report_writing import ReportSummaryWriter

logger = getLogger(__name__)


class DataProcReportSummaryWriter(ReportSummaryWriter):
    test_name = "DataProc"

    @staticmethod
    @log_entry_exit(logger)
    def _add_measured_value_line(writer, req):
        """Override method to convert measured value to a boolean.
        """
        writer.add_line(f"**Measured Value**: {bool(req.meas_value.value)}\n\n")

    @staticmethod
    @log_entry_exit(logger)
    def _add_test_case_supp_info(writer, req):
        """Override method to slightly adjust format of supplementary info for more clean printing.

        Parameters
        ----------
        writer : TocMarkdownWriter
        req : RequirementResults
            The object containing the results for a specific requirement.
        """

        for supp_info_i, supp_info in enumerate(req.l_supp_info):

            writer.add_heading(f"{supp_info.info_key}", depth=2)

            # Trim excess line breaks from the supplementary info's beginning and end
            supp_info_str = supp_info.info_value.strip()

            # Replace single linebreaks with double linebreaks
            supp_info_str = supp_info_str.replace("\n", "\n\n")

            # Replace double linebreaks (which would have been turned into quadruple in the previous step) with a
            # separator between double linebreaks
            supp_info_str = supp_info_str.replace("\n\n\n\n", "\n\n---\n\n")

            # Format PASSED/FAILED in bold
            supp_info_str = supp_info_str.replace(STR_PASS, f"**{STR_PASS}**")
            supp_info_str = supp_info_str.replace(STR_FAIL, f"**{STR_FAIL}**")

            # Add a double newline to the end
            supp_info_str += "\n"

            writer.add_line(supp_info_str)

    @staticmethod
    @log_entry_exit(logger)
    def _add_test_case_figures(*args, **kwargs):
        """Override parent method to exclude figures section, since we don't expect any.
        """
        pass

    @staticmethod
    @log_entry_exit(logger)
    def _add_test_case_textfiles(*args, **kwargs):
        """Override parent method to exclude textfiles section, since we don't expect any.
        """
        pass
