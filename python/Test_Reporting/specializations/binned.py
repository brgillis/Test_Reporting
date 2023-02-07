"""
:file: Test_Reporting/specializations/binned.py

:date: 01/04/2023
:author: Bryan Gillis

Module providing a specialized ReportSummaryWriter for test cases which separate results into bins.
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
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from Test_Reporting.utility.misc import TocMarkdownWriter
from Test_Reporting.utility.product_parsing import SingleTestResult
from Test_Reporting.utility.report_writing import ReportSummaryWriter

STR_TEST_FAILED = "Test failed"
STR_BIN_RESULTS = "Results for bin"

RESULTS_FIGURES_HEADING = "Results and Figures"

GLOBAL_LABEL = "All Data"
BIN_LABEL = "Bin %i"

MSG_NO_FIGURE = "No figure for this bin.\n\n"

REASON_KEY = "REASON"

VAL_SEPARATOR = " = "
RESULT_SEPARATOR = ": "

BIN_MIN_POSITION = 7
BIN_MAX_POSITION = 9

logger = getLogger(__name__)


class BinnedReportSummaryWriter(ReportSummaryWriter):

    def _add_test_case_details_and_figures_with_tmpdir(self, writer: TocMarkdownWriter,
                                                       test_case_results: SingleTestResult, reportdir: str,
                                                       datadir: str, ana_files_tmpdir: str) -> None:
        """Overload of parent method, to implement specialized writing for a test case which parses info from the
        SupplementaryInfo and places figures alongside associated data for each bin.
        """

        writer.add_heading(RESULTS_FIGURES_HEADING, depth=0)

        # Dig out the data for each bin from the SupplementaryInfo
        l_info, l_err_str = self._get_l_info(test_case_results)

        # Check for no data
        if not l_info:
            self._add_no_data_details(writer, test_case_results)
            return

        # Check we have the same number of bins for both slope and intercept
        if not self._check_valid_info(l_info):
            # The info is in an invalid format (determined by the specific test case)
            logger.error("Test results SupplementaryInfo is in invalid format; falling back to default implementation.")
            return super()._add_test_case_details_and_figures_with_tmpdir(writer=writer,
                                                                          test_case_results=test_case_results,
                                                                          reportdir=reportdir, datadir=datadir,
                                                                          ana_files_tmpdir=ana_files_tmpdir)

        # If we have any error messages, print them out
        if l_err_str:
            for line in l_err_str:
                writer.add_line(f"**Error reported:** {line}\n\n")

        self._add_binned_details(writer=writer,
                                 test_case_results=test_case_results,
                                 reportdir=reportdir,
                                 datadir=datadir,
                                 figures_tmpdir=ana_files_tmpdir,
                                 l_info=l_info)

    @staticmethod
    def _check_valid_info(l_info_str):
        """Method-specific check that info is valid. Should be overidden by child classes to implement any necessary
        checks.
        """
        return True

    @staticmethod
    def _add_no_data_details(writer, test_case_results):
        """Method to report details for the case where no test results data is available, including the reason for
        the lack of data.
        """
        writer.add_line("No data available for this test. Reported reason(s):\n\n")
        for si in test_case_results.l_requirements[0].l_supp_info:
            if si.info_key == REASON_KEY:
                writer.add_line(f"* {si.info_value.strip()}\n\n")

    def _add_binned_details(self,
                            writer: TocMarkdownWriter,
                            test_case_results: SingleTestResult,
                            reportdir: str,
                            datadir: str,
                            figures_tmpdir: str,
                            l_info: Sequence, ):
        """Method to write details for test results which is sorted into bins (or just one bin for global
        results), and didn't fail to produce any results.
        """

        # Get the figure label and filename for each bin
        l_figure_labels_and_filenames = self._prepare_ana_files(ana_result=test_case_results.analysis_result,
                                                                reportdir=reportdir, datadir=datadir,
                                                                ana_files_tmpdir=figures_tmpdir)

        # Make a dict of bin indices to filenames

        if l_figure_labels_and_filenames:
            d_figure_filenames = self._get_d_figure_filenames(l_figure_labels_and_filenames)
        else:
            d_figure_filenames = {}

        # Write info for each bin
        for bin_i, info in enumerate(l_info):

            # Check if this is the global test case, which we'll format a bit differently
            is_global = False
            if len(l_info) == 1:
                is_global = True

            if is_global:
                label = GLOBAL_LABEL
            else:
                label = BIN_LABEL % bin_i

            writer.add_heading(label, depth=1)

            # Check if there's a figure for this bin, and prepare and link to it if so

            d_bin_figure_filenames: Union[Optional[str], Dict[Any, Optional[str]]] = d_figure_filenames.get(bin_i)

            # Coerce to list if we just have one filename
            if isinstance(d_bin_figure_filenames, str) or d_bin_figure_filenames is None:
                d_bin_figure_filenames = {None: d_bin_figure_filenames}

            # Trim any Nones from the filename dict
            d_bin_figure_filenames = {k: v for k, v in d_bin_figure_filenames.items() if v is not None}

            self._write_bin_figures_and_info(writer, d_bin_figure_filenames, label, reportdir, figures_tmpdir, info,
                                             is_global)

    def _write_bin_figures_and_info(self,
                                    writer: TocMarkdownWriter,
                                    d_bin_figure_filenames: Union[Optional[str], Dict[Any, Optional[str]]],
                                    label: str,
                                    reportdir: str,
                                    figures_tmpdir: str,
                                    info: Any,
                                    is_global: bool):
        """Write out all info for a given bin. This can be overridden by child classes if desired.

        """
        # Draw all figures for this bin, if we have any. Otherwise, report that we have no figures
        if d_bin_figure_filenames:
            for key, filename in d_bin_figure_filenames.items():
                relative_figure_filename = self._move_ana_file_to_public(filename, reportdir, figures_tmpdir)
                if key:
                    key_label = f" {key}"
                else:
                    key_label = ""
                writer.add_line(f"![{label} Figure{key_label}]({relative_figure_filename})\n\n")
        else:
            writer.add_line(MSG_NO_FIGURE)

        # Use a try block, and any on exception here we'll fall back to simply dumping the SupplementaryInfo as-is
        try:
            self._write_info(writer, info, is_global)
        except Exception as e:
            logger.error("%s", e)
            writer.add_line(f"```\n{info}\n\n```\n")

    @staticmethod
    def _get_d_figure_filenames(l_figure_labels_and_filenames):
        """Parses the figure labels and filenames from a directory and returns a dict appropriately sorting them.
        This may be overridden by child classes if necessary.
        """

        d_figure_filenames = {int(file_info.label.split("-")[-1]): file_info.filename
                              for file_info in l_figure_labels_and_filenames
                              if file_info.is_figure}

        return d_figure_filenames

    def _write_info(self,
                    writer: TocMarkdownWriter,
                    info: Any,
                    is_global: bool):
        """Parses strings containing slope and intercept info for a given bin and writes out the relevant info to a
        provided TocMarkdownWriter.
        """

        # Fix the bin strings for a missing line break that was in older versions
        l_info_lines = info.split("\n")

        # Check if this is global or binned based on the length of the lines list. If binned, output the bin limits
        if not is_global:
            self._write_bin_info(writer, l_info_lines[0])

        # Strip bin info string if present
        if l_info_lines[0].startswith(STR_BIN_RESULTS):
            l_info_lines = l_info_lines[1:]

        # Get the slope and intercept info out of the info strings for this specific bin by properly parsing it. If
        # there's any error with either, fall back to outputting the raw lines.

        try:
            self._parse_and_write_val_info(writer, l_info_lines)
        except Exception as e:
            logger.error("%s", e)
            writer.add_line("```\n")
            for line in l_info_lines:
                writer.add_line(f"{line.strip()}\n")
            writer.add_line("```\n")

    @staticmethod
    def _parse_and_write_val_info(writer: TocMarkdownWriter,
                                  l_info_lines: List[str]) -> None:
        """Parses and writes info for a single bin. Default implementation, which should ideally be overridden by
        child classes.
        """
        writer.add_line("```\n")
        for line in l_info_lines:
            writer.add_line(f"{line.strip()}\n")
        writer.add_line("```\n")

    @staticmethod
    def _get_l_info(test_case_results: SingleTestResult) -> Tuple[List, List]:
        """Gets lists of supplementary info strings for the slope and intercept from the test case results object.
        """

        l_supp_info = test_case_results.l_requirements[0].l_supp_info

        l_info: List[str] = []

        for supp_info in l_supp_info:
            slope_supp_info_str = supp_info.info_value.strip()
            l_info = slope_supp_info_str.split("\n\n")

        # Remove any test failure notifications from the lists, and store them in separate lists
        l_err_str = [s for s in l_info if s.startswith(STR_TEST_FAILED)]
        l_info = [s for s in l_info if not s.startswith(STR_TEST_FAILED)]

        return l_info, l_err_str

    @staticmethod
    def _write_bin_info(writer: TocMarkdownWriter, bin_info_str: str) -> None:
        """Parses a bin info line to get the minimum and maximum limits of the bin and adds a line about it to the
        writer.
        """

        split_bin_info_str = bin_info_str.split()

        bin_min = split_bin_info_str[BIN_MIN_POSITION]
        bin_max = split_bin_info_str[BIN_MAX_POSITION][:-1]

        writer.add_line(f"Bin limits: {bin_min} to {bin_max}.\n\n")
