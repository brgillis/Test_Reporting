"""
:file: Test_Reporting/specializations/cti_gal.py

:date: 11/08/2022
:author: Bryan Gillis

Module providing a specialized ReportSummaryWriter for CTI-Gal test cases.
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
from typing import List, Optional, Tuple

from Test_Reporting.utility.misc import TocMarkdownWriter
from Test_Reporting.utility.product_parsing import SingleTestResult
from Test_Reporting.utility.report_writing import ReportSummaryWriter

RESULTS_FIGURES_HEADING = "Results and Figures"

GLOBAL_LABEL = "Global"
BIN_LABEL = "Bin %i"

MSG_NO_FIGURE = "No figure for this bin.\n\n"

MSG_SLOPE_VAL = "Slope = %s +/- %s\n\n"
MSG_SLOPE_Z = "Z(Slope) = %s (Max allowed: %s)\n\n"
MSG_SLOPE_RESULT = "Slope result: **%s**\n\n"

MSG_INTERCEPT_VAL = "Intercept = %s +/- %s\n\n"
MSG_INTERCEPT_Z = "Z(Intercept) = %s (Max allowed: %s)\n\n"
MSG_INTERCEPT_RESULT = "Intercept result: **%s**\n\n"

SLOPE_INFO_KEY = "SLOPE_INFO"
INTERCEPT_INFO_KEY = "INTERCEPT_INFO"

VAL_SEPARATOR = " = "
RESULT_SEPARATOR = ": "

BIN_MIN_POSITION = 7
BIN_MAX_POSITION = 9

logger = getLogger(__name__)


class CtiGalReportSummaryWriter(ReportSummaryWriter):
    test_name = "CTI-Gal"

    def _add_test_case_details_and_figures_with_tmpdir(self,
                                                       writer: TocMarkdownWriter,
                                                       test_case_results: SingleTestResult,
                                                       reportdir: str,
                                                       tmpdir: str,
                                                       figures_tmpdir: str) -> None:
        """Overload of parent method, to implement specialized writing for the CTI-Gal test case which parses
        slope/intercept info from the SupplementaryInfo and places figures alongside associated data for each bin.
        """

        writer.add_heading(RESULTS_FIGURES_HEADING, depth=0)

        # Dig out the data for each bin from the SupplementaryInfo
        l_slope_bin_str, l_int_bin_str = self._get_slope_intercept_info(test_case_results)

        # Check that data is formatted as expected. If not, fall back to parent implementation
        if (not l_slope_bin_str) or (not l_int_bin_str) or (len(l_slope_bin_str) != len(l_int_bin_str)):
            logger.error(f"CTI-Gal SupplementaryInfo not formatted as expected: {l_slope_bin_str=}, "
                         f"{l_int_bin_str=}. Falling back to parent implementation.")
            return super()._add_test_case_details_and_figures_with_tmpdir(writer=writer,
                                                                          test_case_results=test_case_results,
                                                                          reportdir=reportdir,
                                                                          tmpdir=tmpdir,
                                                                          figures_tmpdir=figures_tmpdir)

        # Get the figure label and filename for each bin
        l_figure_labels_and_filenames = self._prepare_figures(ana_result=test_case_results.analysis_result,
                                                              reportdir=reportdir,
                                                              tmpdir=tmpdir,
                                                              figures_tmpdir=figures_tmpdir)

        # Make a dict of bin indices to filenames
        if l_figure_labels_and_filenames:
            d_figure_filenames = {int(figure_label.split("-")[-1]): figure_filename
                                  for (figure_label, figure_filename) in l_figure_labels_and_filenames}
        else:
            d_figure_filenames = {}

        # Check if this is the global test case, which we'll format a bit differently
        is_global = False
        if len(l_slope_bin_str) == 1:
            is_global = True

        # Write info for each bin
        for bin_i, (slope_str, intercept_str) in enumerate(zip(l_slope_bin_str, l_int_bin_str)):

            if is_global:
                label = GLOBAL_LABEL
            else:
                label = BIN_LABEL % bin_i

            writer.add_heading(label, depth=1)

            # Check if there's a figure for this bin, and prepare and link to it if so
            filename = d_figure_filenames.get(bin_i)
            if filename:
                relative_figure_filename = self._move_figure_to_public(filename, reportdir, figures_tmpdir)
                writer.add_line(f"![{label} Figure]({relative_figure_filename})\n\n")
            else:
                writer.add_line(MSG_NO_FIGURE)

            # Use a try block, and any on exception here we'll fall back to simply dumping the SupplementaryInfo as-is
            try:
                self._write_slope_intercept_info(writer, slope_str, intercept_str, is_global)
            except Exception as e:
                logger.error("%s", e)
                writer.add_line(f"```\n{slope_str}\n\n{intercept_str}\n\n```\n")

    def _write_slope_intercept_info(self,
                                    writer: TocMarkdownWriter,
                                    slope_str: str,
                                    intercept_str: str,
                                    is_global: bool):
        """Parses strings containing slope and intercept info for a given bin and writes out the relevant info to a
        provided TocMarkdownWriter.
        """

        # Fix the bin strings for a missing line break that was in older versions
        slope_str = self._fix_bin_str(slope_str)
        intercept_str = self._fix_bin_str(intercept_str)
        l_slope_info_lines = slope_str.split("\n")
        l_intercept_info_lines = intercept_str.split("\n")

        # Check if this is global or binned based on the length of the lines list. If binned, output the bin
        # limits and adjust `l_info_lines` and `l_intercept_info_lines` to match the format it would be for
        # the global case
        if not is_global:
            self._write_bin_info(writer, l_slope_info_lines[0])
            l_slope_info_lines = l_slope_info_lines[1:]
            l_intercept_info_lines = l_intercept_info_lines[1:]

        # Get the slope and intercept info out of the info strings for this specific bin by properly parsing it. If
        # there's any error with either, fall back to outputting the raw lines.

        for (l_info_lines, msg_val,
             msg_z, msg_result) in ((l_slope_info_lines, MSG_SLOPE_VAL, MSG_SLOPE_Z, MSG_SLOPE_RESULT),
                                    (l_intercept_info_lines, MSG_INTERCEPT_VAL, MSG_INTERCEPT_Z, MSG_INTERCEPT_RESULT)):
            try:
                self._parse_and_write_val_info(writer, l_info_lines, msg_val, msg_z, msg_result)
            except Exception as e:
                logger.error("%s", e)
                writer.add_line("```\n")
                for line in l_info_lines:
                    writer.add_line(f"{line.strip()}\n")
                writer.add_line("```\n")

    @staticmethod
    def _parse_and_write_val_info(writer: TocMarkdownWriter,
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
    def _get_slope_intercept_info(test_case_results: SingleTestResult) -> Tuple[Optional[List[str]],
                                                                                Optional[List[str]]]:
        """Gets lists of supplementary info strings for the slope and intercept from the test case results object.
        """

        l_supp_info = test_case_results.l_requirements[0].l_supp_info

        l_slope_bin_str: Optional[List[str]] = None
        l_int_bin_str: Optional[List[str]] = None

        for supp_info in l_supp_info:
            if supp_info.info_key == SLOPE_INFO_KEY:
                slope_supp_info_str = supp_info.info_value.strip()
                l_slope_bin_str = slope_supp_info_str.split("\n\n")
            elif supp_info.info_key == INTERCEPT_INFO_KEY:
                int_supp_info_str = supp_info.info_value.strip()
                l_int_bin_str = int_supp_info_str.split("\n\n")

        return l_slope_bin_str, l_int_bin_str

    @staticmethod
    def _fix_bin_str(bin_str: str) -> str:
        """Fixes a bin string for a bug that was present in old code (if found to be present here), where a linebreak
        was missing.
        """
        bin_str = bin_str.replace(":slope", ":\nslope")
        bin_str = bin_str.replace(":intercept", ":\nintercept")
        return bin_str

    @staticmethod
    def _write_bin_info(writer: TocMarkdownWriter, bin_info_str: str) -> None:
        """Parses a bin info line to get the minimum and maximum limits of the bin and adds a line about it to the
        writer.
        """

        split_bin_info_str = bin_info_str.split()

        bin_min = split_bin_info_str[BIN_MIN_POSITION]
        bin_max = split_bin_info_str[BIN_MAX_POSITION]

        writer.add_line(f"Bin limits: {bin_min} to {bin_max}.\n\n")
