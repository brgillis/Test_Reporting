"""
:file: utility/misc.py

:date: 10/18/2022
:author: Bryan Gillis

Module for miscellaneous utility functions and classes used in this project.
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

from __future__ import annotations

import codecs
import hashlib
import logging
import re
import subprocess
from typing import List, TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from logging import Logger
    from typing import Callable  # noqa F401

logger = logging.getLogger(__name__)


def log_entry_exit(my_logger, level=logging.DEBUG):
    """Decorator which, when applied to a function, will log upon entry/exit of the function the name of the
    function, the arguments provided to it, and the output of it.

    Parameters
    ----------
    my_logger : Logger
        The logger to use for logging the info about this function.
    level : int, default=logging.DEBUG
        The level at which to log. Default: DEBUG

    Returns
    -------
    Callable
    """

    def func_wrap(func):
        def wrap(*args, **kwargs):
            my_logger.log(level, "Entering method `%s` with positional arguments `%s` and keyword arguments `%s`.",
                          func.__qualname__, args, kwargs)
            output = func(*args, **kwargs)
            my_logger.log(level, "Exiting method `%s` with output `%s`.", func.__qualname__, output)

            return output

        return wrap

    return func_wrap


@log_entry_exit(logger)
def extract_tarball(qualified_results_tarball_filename, qualified_tmpdir):
    """Extracts a tarball into the provided directory, performing security checks on the provided filename to ensure
    it doesn't contain any characters which are potentially unsafe in a `tar` command.

    Parameters
    ----------
    qualified_results_tarball_filename : str
        The fully-qualified filename of a tarball containing the test results product and associated datafiles.
    qualified_tmpdir : str
        The fully-qualified path to a temporary directory which can be used for this function.
    """

    # Silently coerce the input to strings
    qualified_results_tarball_filename = str(qualified_results_tarball_filename)
    qualified_tmpdir = str(qualified_tmpdir)

    # Check the filename contains only expected characters. If it doesn't, this could open a security hole
    filename_regex_match = re.match(r"^[a-zA-Z0-9\-_./+]*\.tar(\.gz)?$", qualified_results_tarball_filename)

    if not filename_regex_match:
        raise ValueError(f"Qualified filename {qualified_results_tarball_filename} failed security check. It must"
                         f"contain only alphanumeric characters and [-_./+], and must end with .tar or .tar.gz.")

    # Ditto for the directory being used
    tmpdir_regex_match = re.match(r"^[a-zA-Z0-9\-_./+]*$", qualified_tmpdir)

    if not tmpdir_regex_match:
        raise ValueError(f"Qualified tempdir {qualified_tmpdir} failed security check. It must"
                         f"contain only alphanumeric characters and [-_./+].")

    cmd = f"cd {qualified_tmpdir} && tar -xf {qualified_results_tarball_filename}"
    tar_results = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if tar_results.returncode:
        if "No such file" in str(tar_results.stderr):
            raise FileNotFoundError(tar_results.stderr)
        raise ValueError(f"Un-tarring of {qualified_results_tarball_filename} failed. stderr from tar "
                         f"process was: {tar_results.stderr}")


@log_entry_exit(logger)
def hash_any(obj, max_length=None):
    """Hashes any immutable object into a base64 string of a given length.

    Parameters
    ----------
    obj : Any immutable
        The object to be hashed.
    max_length : int or None, default=None
        This limits the maximum length of the string to return. If None (default), the full hash will be returned.

    Returns
    -------
    hash : str
    """

    full_hash = hashlib.sha256(repr(obj).encode()).hexdigest()

    # Recode it into base 64. Note that this results in a stray newline character
    # at the end, so we remove that.
    full_hash = codecs.encode(codecs.decode(full_hash, 'hex'), 'base64')[:-1]

    # This also allows the / character which we can't use, so replace it with .
    # Also decode it into a standard string
    full_hash = full_hash.decode().replace("/", ".")

    if max_length is not None and len(full_hash) > max_length:
        full_hash = full_hash[:max_length]

    return full_hash


class TocMarkdownWriter:
    """Class to help with writing Markdown files which include a Table of Contents.
    """

    @log_entry_exit(logger)
    def __init__(self, title):
        """Initializes this writer, setting the desired title of the page.

        Parameters
        ----------
        title : str
            The desired title for this page. This does not need to include any leading '#'s or surrounding whitespace.
        """

        # Strip any leading '#' and any enclosing whitespace from the title, so we can be sure it's properly formatted
        while title.startswith('#'):
            title = title[1:]
        self.title = title.strip()

        self._l_lines: List[str] = []
        self._l_toc_lines: List[str] = []

    @log_entry_exit(logger)
    def add_line(self, line):
        """Add a standard line to be written as part of the body text of the file. Note that this class does not
        automatically add linebreaks after lines, so the line added here must include any desired linebreaks. This
        can be thought of as acting like the `write` method of a filehandle opened to write or append.

        Parameters
        ----------
        line : str
            The line to be written, including any desired linebreaks afterwards.
        """
        self._l_lines.append(line)

    @log_entry_exit(logger)
    def add_heading(self, heading, depth):
        """Add a heading line to be included at this point in the file, which will also be linked from the table-of
        contents.

        Parameters
        ----------
        heading : str
            The heading to be added both to the Table of Contents and the section header in the body of the file.
            This should not include any leading '#'s or surrounding whitespace.
        depth : int
            Integer >= 0 specifying the depth of the heading. Depth 0 corresponds to the highest allowed depth within
            the body of the file (a heading starting with '## '), and each increase of depth by 1 corresponds to a
            section which will have an extra '#' in its header, so e.g. depth 2 would start with '#### '.
        """

        # Trim any beginning '#'s and spaces, as those will be added automatically at the proper depth
        input_heading = heading
        hash_counter = 0
        while heading.startswith("#"):
            heading = heading[1:]
            hash_counter += 1

        # If any '#'s were included, check that they're consistent with the specified depth, and raise an exception
        # if not as it will be unclear what the user desired in this case.
        if (hash_counter > 0) and (hash_counter != depth + 2):
            raise ValueError(f"Heading '{input_heading}' has inconsistent number of '#'s with specified depth ("
                             f"{depth}). Heading should be supplied without any leading '#'s, with depth used to "
                             "control this.")

        heading = heading.strip()

        # Make sure the label for this heading is unique by appending to it a counter of the number of headings
        # already in the document
        label = f"{heading.lower().replace(' ', '-')}-{len(self._l_toc_lines)}"

        # Add a line for this heading both in the main list of lines (so it will be written at the proper location)
        # and in the lines for the Table of Contents, both formatted properly and with the label linking them
        self._l_lines.append("#" * (depth + 2) + f" {heading} <a id=\"{label}\"></a>\n\n")
        self._l_toc_lines.append("  " * depth + f"1. [{heading}](#{label})\n")

    @log_entry_exit(logger)
    def write(self, fo: TextIO):
        """Writes out the TOC and all lines added to this object.

        Parameters
        ----------
        fo : TextIO
            The text filehandle to write to.
        """

        fo.write(f"# {self.title}\n\n")

        # Only write a Table of Contents if there's more than one heading; otherwise it's not worth it
        if len(self._l_toc_lines) > 1:

            fo.write(f"## Table of Contents\n\n")

            for line in self._l_toc_lines:
                fo.write(line)

            fo.write("\n")

        for line in self._l_lines:
            fo.write(line)
