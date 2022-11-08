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

from utility.test_writing import TestSummaryWriter


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
        req = test_case_results.l_requirements[0]

        slope_supp_info_str = req.l_supp_info[0].info_value.strip()
        l_slope_bin_str = slope_supp_info_str.split("\n\n")

        int_supp_info_str = req.l_supp_info[1].info_value.strip()
        l_int_bin_str = int_supp_info_str.split("\n\n")

        # Get the figure label and filename for each bin
        l_figure_labels_and_filenames = self._prepare_figures(test_case_results.analysis_result, rootdir, tmpdir,
                                                              figures_tmpdir)

        # Make a dict of bin indices to filenames
        d_figure_filenames = {int(figure_label.split("-")[-1]): figure_filename
                              for (figure_label, figure_filename) in l_figure_labels_and_filenames}

        # Write info for each bin
        for bin_i, (slope_str, int_str) in enumerate(zip(l_slope_bin_str, l_int_bin_str)):

            filename = d_figure_filenames[bin_i]

            relative_figure_filename = self._move_figure_to_public(filename, rootdir, figures_tmpdir)

            bin_label = f"Bin {bin_i}"
            writer.add_heading(bin_label, depth=1)

            # Add a link to the figure
            writer.add_line(f"![{bin_label}]({relative_figure_filename})\n\n")

            # Fix the bin strings for a missing line break that was in older versions
            slope_str = self._fix_bin_str(slope_str)
            int_str = self._fix_bin_str(int_str)

            # Get the slope and intercept info out of the info strings for this specific bin by properly parsing it
            l_slope_info_lines = slope_str.split("\n")
            slope = l_slope_info_lines[1].split(" = ")[1]
            slope_err = l_slope_info_lines[2].split(" = ")[1]
            slope_z = l_slope_info_lines[3].split(" = ")[1]
            max_slope_z = l_slope_info_lines[4].split(" = ")[1]
            slope_result = l_slope_info_lines[5].split(": ")[1]

            l_int_info_lines = int_str.split("\n")
            intercept = l_int_info_lines[1].split(" = ")[1]
            intercept_err = l_int_info_lines[2].split(" = ")[1]
            intercept_z = l_int_info_lines[3].split(" = ")[1]
            max_intercept_z = l_int_info_lines[4].split(" = ")[1]
            intercept_result = l_int_info_lines[5].split(": ")[1]

            # Write out the slope and intercept info for this bin
            writer.add_line(f"Slope = {slope} +/- {slope_err}\n\n")
            writer.add_line(f"Z(Slope) = {slope_z} (Max allowed: {max_slope_z})\n\n")
            writer.add_line(f"Slope result: **{slope_result}**\n\n")
            writer.add_line(f"Intercept = {intercept} +/- {intercept_err}\n\n")
            writer.add_line(f"Z(Intercept) = {intercept_z} (Max allowed: {max_intercept_z})\n\n")
            writer.add_line(f"Intercept result: **{intercept_result}**\n\n")

    def _fix_bin_str(self, bin_str):
        """Fixes a bin string for a bug that was present in old code (if found to be present here), where a linebreak
        was missing.

        Parameters
        ----------
        bin_str : str

        Returns
        -------
        fixed_bin_str : str
        """
        return bin_str.replace(":slope", ":\nslope")
