"""
:file: utility/figures.py

:date: 11/02/2022
:author: Bryan Gillis

This python module provides functions to aid in managing figures associated with test cases.
"""
import os
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

from typing import List, Optional, Tuple

DIRECTORY_EXT = ".txt"
DIRECTORY_FIGURES_HEADER = "# Figures:"
DIRECTORY_SEPARATOR = ": "


def find_directory_filename(figures_tmpdir):
    """

    Parameters
    ----------
    figures_tmpdir : str

    Returns
    -------
    qualified_directory_filename : str
    """

    l_filenames = os.listdir(figures_tmpdir)

    l_possible_directory_filenames: List[str] = []
    for filename in l_filenames:
        if filename.endswith(DIRECTORY_EXT):
            l_possible_directory_filenames.append(filename)

    # Check we have exactly one possibility, otherwise raise an exception
    if len(l_possible_directory_filenames) == 1:
        return l_possible_directory_filenames[0]
    elif len(l_possible_directory_filenames) == 0:
        raise FileNotFoundError(f"No identifiable directory file found in directory {figures_tmpdir}.")
    else:
        raise ValueError(
            f"Multiple possible directory files found in directory {figures_tmpdir}: {l_possible_directory_filenames}")


def read_figure_labels_and_filenames(qualified_directory_filename):
    """Reads a directory file, and returns a list of figure labels and filenames. Note that any figure label might be
    None if it's not supplied in the directory file.

    Parameters
    ----------
    qualified_directory_filename : str
        The fully-qualified path to the directory file.

    Returns
    -------
    l_figure_labels_and_filenames: List[Tuple[str or None, str]]
    """

    # Use the directory to find labels for figures, if it has them. Otherwise, just use it as a list of the figures
    with open(qualified_directory_filename, "r") as fi:
        l_directory_lines = fi.readlines()

    l_figure_labels_and_filenames: List[Tuple[Optional[str], str]] = []
    figures_section_started = False
    for directory_line in l_directory_lines:
        directory_line = directory_line.strip()

        # If we haven't started the figures section, check for the header which starts it and then start reading
        # on the next iteration
        if not figures_section_started:
            if directory_line == DIRECTORY_FIGURES_HEADER:
                figures_section_started = True
            continue

        # If we get here, we're in the figures section
        figure_label: Optional[str] = None
        figure_filename: str
        if DIRECTORY_SEPARATOR in directory_line:
            figure_label, figure_filename = directory_line.split(DIRECTORY_SEPARATOR)
        else:
            figure_filename = directory_line
        l_figure_labels_and_filenames.append((figure_label, figure_filename))

    return l_figure_labels_and_filenames
