"""
:file: specializations/cti_gal.py

:date: 11/08/2022
:author: Bryan Gillis

Module providing a specialized TestSummaryWriter for CTI-Gal test cases.
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

from utility.misc import TocMarkdownWriter
from utility.product_parsing import SingleTestResult
from utility.test_writing import TestSummaryWriter

GLOBAL_LABEL = "Global"
BIN_LABEL = "Bin %i"

MSG_NO_FIGURE = "No figure for this bin.\n\n"

MSG_SLOPE_VAL = "Slope = %f +/- %f\n\n"
MSG_SLOPE_Z = "Z(Slope) = %f (Max allowed: %f)\n\n"
MSG_SLOPE_RESULT = "Slope result: **%f**\n\n"

MSG_INTERCEPT_VAL = "Intercept = %f +/- %f\n\n"
MSG_INTERCEPT_Z = "Z(Intercept) = %f (Max allowed: %f)\n\n"
MSG_INTERCEPT_RESULT = "Intercept result: **%f**\n\n"

SLOPE_INFO_KEY = "SLOPE_INFO"
INTERCEPT_INFO_KEY = "INTERCEPT_INFO"

VAL_SEPARATOR = " = "
RESULT_SEPARATOR = ": "

BIN_MIN_POSITION = 7
BIN_MAX_POSITION = 9

logger = getLogger(__name__)


class CtiGalTestSummaryWriter(TestSummaryWriter):
    test_name = "CTI-Gal"

    def _add_test_case_details_and_figures_with_tmpdir(self,
                                                       writer,
                                                       test_case_results,
                                                       rootdir,
                                                       tmpdir,
                                                       figures_tmpdir):
        writer.add_heading("Results and Figures", depth=0)

        # Dig out the data for each bin from the SupplementaryInfo
        l_slope_bin_str, l_int_bin_str = self._get_slope_intercept_info(test_case_results)

        # Check that data is formatted as expected. If not, fall back to parent implementation
        if (not l_slope_bin_str) or (not l_int_bin_str) or (len(l_slope_bin_str) != len(l_int_bin_str)):
            logger.error(f"CTI-Gal SupplementaryInfo not formatted as expected: {l_slope_bin_str=}, "
                         f"{l_int_bin_str=}. Falling back to parent implementation.")
            return super()._add_test_case_details_and_figures_with_tmpdir(writer,
                                                                          test_case_results,
                                                                          rootdir,
                                                                          tmpdir,
                                                                          figures_tmpdir)

        # Get the figure label and filename for each bin
        l_figure_labels_and_filenames = self._prepare_figures(test_case_results.analysis_result, rootdir, tmpdir,
                                                              figures_tmpdir)

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
        for bin_i, (slope_str, int_str) in enumerate(zip(l_slope_bin_str, l_int_bin_str)):

            if is_global:
                label = GLOBAL_LABEL
            else:
                label = BIN_LABEL % bin_i
            writer.add_heading(label, depth=1)

            filename = d_figure_filenames.get(bin_i)

            # Check if there's a figure for this bin, and prepare and link to it if so
            if filename:
                relative_figure_filename = self._move_figure_to_public(filename, rootdir, figures_tmpdir)
                writer.add_line(f"![{label}]({relative_figure_filename})\n\n")
            else:
                writer.add_line(MSG_NO_FIGURE)

            # Use a try block, and any exception here we'll fall back to simply dumping the SupplementaryInfo as-is

            try:
                # Fix the bin strings for a missing line break that was in older versions
                slope_str = self._fix_bin_str(slope_str)
                int_str = self._fix_bin_str(int_str)

                l_slope_info_lines = slope_str.split("\n")
                l_int_info_lines = int_str.split("\n")

                # Check if this is global or binned based on the length of the lines list. If binned, output the bin
                # limits and adjust `l_slope_info_lines` and `l_int_info_lines` to match the format it would be for
                # the global case
                if not is_global:
                    self._write_bin_info(writer, l_slope_info_lines[0])
                    l_slope_info_lines = l_slope_info_lines[1:]
                    l_int_info_lines = l_int_info_lines[1:]

                # Get the slope and intercept info out of the info strings for this specific bin by properly parsing it
                slope = l_slope_info_lines[0].split(VAL_SEPARATOR)[1]
                slope_err = l_slope_info_lines[1].split(VAL_SEPARATOR)[1]
                slope_z = l_slope_info_lines[2].split(VAL_SEPARATOR)[1]
                max_slope_z = l_slope_info_lines[3].split(VAL_SEPARATOR)[1]
                slope_result = l_slope_info_lines[4].split(RESULT_SEPARATOR)[1]

                intercept = l_int_info_lines[0].split(VAL_SEPARATOR)[1]
                intercept_err = l_int_info_lines[1].split(VAL_SEPARATOR)[1]
                intercept_z = l_int_info_lines[2].split(VAL_SEPARATOR)[1]
                max_intercept_z = l_int_info_lines[3].split(VAL_SEPARATOR)[1]
                intercept_result = l_int_info_lines[4].split(RESULT_SEPARATOR)[1]

                # Write out the slope and intercept info for this bin
                writer.add_line(MSG_SLOPE_VAL % slope, slope_err)
                writer.add_line(MSG_SLOPE_Z % slope_z, max_slope_z)
                writer.add_line(MSG_SLOPE_RESULT % slope_result)
                writer.add_line(MSG_INTERCEPT_VAL % intercept, intercept_err)
                writer.add_line(MSG_INTERCEPT_Z % intercept_z, max_intercept_z)
                writer.add_line(MSG_INTERCEPT_RESULT % intercept_result)

            except Exception as e:
                logger.error("%s", e)

                writer.add_line("```\n")
                writer.add_line(f"{slope_str}\n\n")
                writer.add_line(f"{int_str}\n\n")
                writer.add_line("```\n")

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
