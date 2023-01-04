"""
:file: Test_Reporting/specializations/cti_gal.py

:date: 11/08/2022
:author: Bryan Gillis

Module providing a specialized ReportSummaryWriter for CTI-Gal test cases.
"""
from dataclasses import dataclass
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
from typing import List, Sequence, Tuple

from Test_Reporting.specializations.binned import (BinnedReportSummaryWriter, RESULT_SEPARATOR, STR_BIN_RESULTS,
                                                   STR_TEST_FAILED, VAL_SEPARATOR, )
from Test_Reporting.utility.misc import TocMarkdownWriter
from Test_Reporting.utility.product_parsing import SingleTestResult
from Test_Reporting.utility.report_writing import ReportSummaryWriter

MSG_SLOPE_VAL = "Slope = %s +/- %s\n\n"
MSG_SLOPE_Z = "Z(Slope) = %s (Max allowed: %s)\n\n"
MSG_SLOPE_RESULT = "Slope result: **%s**\n\n"

MSG_INTERCEPT_VAL = "Intercept = %s +/- %s\n\n"
MSG_INTERCEPT_Z = "Z(Intercept) = %s (Max allowed: %s)\n\n"
MSG_INTERCEPT_RESULT = "Intercept result: **%s**\n\n"

SLOPE_INFO_KEY = "SLOPE_INFO"
INTERCEPT_INFO_KEY = "INTERCEPT_INFO"
REASON_KEY = "REASON"

logger = getLogger(__name__)


@dataclass
class SlopeInterceptInfo:
    slope_str: str
    intercept_str: str


class CtiGalReportSummaryWriter(BinnedReportSummaryWriter):
    test_name = "CTI-Gal"

    def _write_info(self,
                    writer: TocMarkdownWriter,
                    info: SlopeInterceptInfo,
                    is_global: bool):
        """Parses strings containing slope and intercept info for a given bin and writes out the relevant info to a
        provided TocMarkdownWriter.
        """

        # Fix the bin strings for a missing line break that was in older versions
        slope_str = self._fix_bin_str(info.slope_str)
        intercept_str = self._fix_bin_str(info.intercept_str)
        l_slope_info_lines = slope_str.split("\n")
        l_intercept_info_lines = intercept_str.split("\n")

        # Check if this is global or binned based on the length of the lines list. If binned, output the bin limits
        if not is_global:
            self._write_bin_info(writer, l_slope_info_lines[0])

        # Strip bin info string if present
        if l_slope_info_lines[0].startswith(STR_BIN_RESULTS):
            l_slope_info_lines = l_slope_info_lines[1:]
        if l_intercept_info_lines[0].startswith(STR_BIN_RESULTS):
            l_intercept_info_lines = l_intercept_info_lines[1:]

        # Get the slope and intercept info out of the info strings for this specific bin by properly parsing it. If
        # there's any error with either, fall back to outputting the raw lines.

        for (l_info_lines, msg_val,
             msg_z, msg_result) in ((l_slope_info_lines, MSG_SLOPE_VAL, MSG_SLOPE_Z, MSG_SLOPE_RESULT),
                                    (l_intercept_info_lines, MSG_INTERCEPT_VAL, MSG_INTERCEPT_Z, MSG_INTERCEPT_RESULT)):
            try:
                self._parse_and_write_slope_intercept_info(writer, l_info_lines, msg_val, msg_z, msg_result)
            except Exception as e:
                logger.error("%s", e)
                writer.add_line("```\n")
                for line in l_info_lines:
                    writer.add_line(f"{line.strip()}\n")
                writer.add_line("```\n")

    @staticmethod
    def _parse_and_write_slope_intercept_info(writer: TocMarkdownWriter,
                                              l_info_lines: List[str],
                                              msg_val: str,
                                              msg_z: str,
                                              msg_result: str) -> None:
        """Parses and writes info for either the slope or intercept.
        """

        val = l_info_lines[0].split(VAL_SEPARATOR)[1]
        val_err = l_info_lines[1].split(VAL_SEPARATOR)[1]
        val_z = l_info_lines[2].split(VAL_SEPARATOR)[1]
        max_val_z = l_info_lines[3].split(VAL_SEPARATOR)[1]
        val_result = l_info_lines[4].split(RESULT_SEPARATOR)[1]

        writer.add_line(msg_val % (val, val_err))
        writer.add_line(msg_z % (val_z, max_val_z))
        writer.add_line(msg_result % val_result)

    @staticmethod
    def _get_l_info(test_case_results: SingleTestResult) -> Tuple[List[SlopeInterceptInfo],
                                                                  List[str]]:
        """Gets lists of supplementary info strings for the slope and intercept from the test case results object.
        """

        l_supp_info = test_case_results.l_requirements[0].l_supp_info

        l_slope_bin_str: List[str] = []
        l_int_bin_str: List[str] = []

        for supp_info in l_supp_info:
            if supp_info.info_key == SLOPE_INFO_KEY:
                slope_supp_info_str = supp_info.info_value.strip()
                l_slope_bin_str = slope_supp_info_str.split("\n\n")
            elif supp_info.info_key == INTERCEPT_INFO_KEY:
                int_supp_info_str = supp_info.info_value.strip()
                l_int_bin_str = int_supp_info_str.split("\n\n")

        # Remove any test failure notifications from the lists, and store them in separate lists
        l_slope_err_str = [s for s in l_slope_bin_str if s.startswith(STR_TEST_FAILED)]
        l_slope_bin_str = [s for s in l_slope_bin_str if not s.startswith(STR_TEST_FAILED)]

        l_int_err_str = [s for s in l_int_bin_str if s.startswith(STR_TEST_FAILED)]
        l_int_bin_str = [s for s in l_int_bin_str if not s.startswith(STR_TEST_FAILED)]

        # Combine results into expected output format
        l_info = [SlopeInterceptInfo(a[0], a[1]) for a in zip(l_slope_bin_str, l_int_bin_str)]
        l_err_str = [*l_slope_err_str, *l_int_err_str]

        return l_info, l_err_str

    @staticmethod
    def _fix_bin_str(bin_str: str) -> str:
        """Fixes a bin string for a bug that was present in old code (if found to be present here), where a linebreak
        was missing.
        """
        bin_str = bin_str.replace(":slope", ":\nslope")
        bin_str = bin_str.replace(":intercept", ":\nintercept")
        return bin_str
