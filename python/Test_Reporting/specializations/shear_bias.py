"""
:file: Test_Reporting/specializations/shear_bias.py

:date: 01/05/2023
:author: Bryan Gillis

Module providing a specialized ReportSummaryWriter for Shear Bias test cases.
"""
import re
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
from typing import Dict, List, Tuple

from Test_Reporting.specializations.binned import (BinnedReportSummaryWriter, RESULT_SEPARATOR, STR_BIN_RESULTS,
                                                   STR_TEST_FAILED,
                                                   VAL_SEPARATOR, )
from Test_Reporting.utility.misc import TocMarkdownWriter, log_entry_exit
from Test_Reporting.utility.product_parsing import SingleTestResult, TestResults

logger = getLogger(__name__)

M_REQ = "R-SHE-CAL-F-070"
C_REQ = "R-SHE-CAL-F-080"

STR_REPLACE_BIAS = "$REPLACEME_BIAS"
STR_REPLACE_COMP = "$REPLACEME_COMP"
STR_REPLACE_BIAS_COMP = f"{STR_REPLACE_BIAS}<sub>{STR_REPLACE_COMP}</sub>"

MSG_B_VAL = f"{STR_REPLACE_BIAS_COMP} = %s +/- %s\n\n"
MSG_B_Z = f"Z({STR_REPLACE_BIAS_COMP}) = %s (Max allowed: %s)\n\n"
MSG_B_RESULT = f"{STR_REPLACE_BIAS_COMP} result: **%s**\n\n"

G1_INFO_KEY = "G1_INFO"
G2_INFO_KEY = "G2_INFO"


@dataclass
class BiasInfo:
    g1_str: str
    g2_str: str
    bias: str


class ShearBiasReportSummaryWriter(BinnedReportSummaryWriter):
    test_name = "Shear-Bias"

    @staticmethod
    @log_entry_exit(logger)
    def _get_l_test_case_names(test_results: TestResults, test_name_tail: str):
        """Since this test case has multiple binned tests, each with the same Test Case ID, we want to modify how
        names of reports are generated to include the parameter used for binning.
        """

        d_test_name_instances: Dict[str, int] = {}
        l_test_case_names: List[str] = []

        for test_case_results in test_results.l_test_results:

            test_case_id = test_case_results.test_id

            # Use a Regex match on the test description to determine what binning is used
            bin_parameter_regex_match = re.match(r".*Binned by ([a-zA-Z0-9./_\-]+)\..*",
                                                 test_case_results.test_description)
            if bin_parameter_regex_match:
                test_case_root_name = f"{test_case_id}-{bin_parameter_regex_match.groups()[0]}"
            elif re.match(r".*Binned by background level\..*", test_case_results.test_description):
                # Check also for the phrase "background level", which for some reason is written out fully, unlike other
                # bin parameters
                test_case_root_name = f"{test_case_id}-BG"
            else:
                logger.error("Could not determine binning parameter from test description: "
                             f"\"{test_case_results.test_description}\"")
                test_case_root_name = test_case_id

            if test_case_root_name in d_test_name_instances:
                d_test_name_instances[test_case_root_name] += 1
                test_case_name = f"{test_case_root_name}-{d_test_name_instances[test_case_root_name]}{test_name_tail}"
            else:
                d_test_name_instances[test_case_root_name] = 1
                test_case_name = f"{test_case_root_name}{test_name_tail}"

            l_test_case_names.append(test_case_name)

        return l_test_case_names

    @log_entry_exit(logger)
    def _write_info(self,
                    writer: TocMarkdownWriter,
                    info: BiasInfo,
                    is_global: bool):
        """Parses strings containing g1 and g2 bias info for a given bin and writes out the relevant info to a
        provided TocMarkdownWriter.
        """

        # Fix the bin strings for a missing line break that was in older versions
        g1_str = self._fix_bin_str(info.g1_str)
        g2_str = self._fix_bin_str(info.g2_str)
        l_g1_info_lines = g1_str.split("\n")
        l_g2_info_lines = g2_str.split("\n")

        # Check if this is global or binned based on the length of the lines list. If binned, output the bin limits
        if not is_global:
            self._write_bin_info(writer, l_g1_info_lines[0])

        # Strip bin info string if present
        if l_g1_info_lines[0].startswith(STR_BIN_RESULTS):
            l_g1_info_lines = l_g1_info_lines[1:]
        if l_g2_info_lines[0].startswith(STR_BIN_RESULTS):
            l_g2_info_lines = l_g2_info_lines[1:]

        # Get the g1 and g2 info out of the info strings for this specific bin by properly parsing it. If
        # there's any error with either, fall back to outputting the raw lines.

        for l_info_lines, comp_index in ((l_g1_info_lines, 1), (l_g2_info_lines, 2)):
            try:
                self._parse_and_write_g1_g2_info(writer, l_info_lines, info.bias, comp_index)
            except Exception as e:
                logger.error("%s", e)
                writer.add_line("```\n")
                for line in l_info_lines:
                    writer.add_line(f"{line.strip()}\n")
                writer.add_line("```\n")

    @staticmethod
    @log_entry_exit(logger)
    def _parse_and_write_g1_g2_info(writer: TocMarkdownWriter,
                                    l_info_lines: List[str],
                                    bias: str,
                                    comp_index: int) -> None:
        """Parses and writes info for the bias component.
        """

        val = l_info_lines[0].split(VAL_SEPARATOR)[1]
        val_err = l_info_lines[1].split(VAL_SEPARATOR)[1]
        val_z = l_info_lines[2].split(VAL_SEPARATOR)[1]
        max_val_z = l_info_lines[3].split(VAL_SEPARATOR)[1]
        val_result = l_info_lines[4].split(RESULT_SEPARATOR)[1]

        msg_val = MSG_B_VAL.replace(STR_REPLACE_BIAS, bias).replace(STR_REPLACE_COMP, str(comp_index))
        writer.add_line(msg_val % (val, val_err))

        msg_z = MSG_B_Z.replace(STR_REPLACE_BIAS, bias).replace(STR_REPLACE_COMP, str(comp_index))
        writer.add_line(msg_z % (val_z, max_val_z))

        msg_result = MSG_B_RESULT.replace(STR_REPLACE_BIAS, bias).replace(STR_REPLACE_COMP, str(comp_index))
        writer.add_line(msg_result % val_result)

    @staticmethod
    @log_entry_exit(logger)
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

    @staticmethod
    @log_entry_exit(logger)
    def _get_l_info(test_case_results: SingleTestResult) -> Tuple[List[BiasInfo],
                                                                  List[str]]:
        """Gets lists of supplementary info strings for the slope and intercept from the test case results object.
        """

        req = test_case_results.l_requirements[0]
        req_id = req.req_id

        if req_id == M_REQ:
            bias = "m"
        elif req_id == C_REQ:
            bias = "c"
        else:
            raise ValueError(f"Requirement {req_id} is not recognized to be associated with either m or c bias.")

        l_supp_info = req.l_supp_info

        l_g1_bin_str: List[str] = []
        l_g2_bin_str: List[str] = []

        for supp_info in l_supp_info:

            supp_info_str = supp_info.info_value.strip()

            # Remove the first line, which doesn't contain any relevant information for us (use length + 2 to include
            # the
            # \n at the end of the line
            len_first_line = len(supp_info_str.split('\n')[0])
            supp_info_str = supp_info_str[len_first_line + 2:]

            if supp_info.info_key == G1_INFO_KEY:
                l_g1_bin_str = supp_info_str.split("\n\n")
            elif supp_info.info_key == G2_INFO_KEY:
                l_g2_bin_str = supp_info_str.split("\n\n")

        # Remove any test failure notifications from the lists, and store them in separate lists
        l_g1_err_str = [s for s in l_g1_bin_str if s.startswith(STR_TEST_FAILED)]
        l_g1_bin_str = [s for s in l_g1_bin_str if not s.startswith(STR_TEST_FAILED)]

        l_g2_err_str = [s for s in l_g2_bin_str if s.startswith(STR_TEST_FAILED)]
        l_g2_bin_str = [s for s in l_g2_bin_str if not s.startswith(STR_TEST_FAILED)]

        # Combine results g2o expected output format
        l_info = [BiasInfo(a[0], a[1], bias) for a in zip(l_g1_bin_str, l_g2_bin_str)]
        l_err_str = [*l_g1_err_str, *l_g2_err_str]

        return l_info, l_err_str

    @staticmethod
    @log_entry_exit(logger)
    def _fix_bin_str(bin_str: str) -> str:
        """Fixes a bin string for a bug that was present in old code (if found to be present here), where a linebreak
        was missing.
        """
        bin_str = bin_str.replace(":m", ":\nm")
        bin_str = bin_str.replace(":c", ":\nc")
        return bin_str
