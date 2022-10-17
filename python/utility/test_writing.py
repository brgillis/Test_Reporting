"""
:file: utility/test_writing.py

:date: 10/17/2022
:author: Bryan Gillis

This python module provides functionality for writing the test summary markdown files. To allow customization for
individual unit tests, a callable class, TestSummaryWriter, is used, with its call being a template method where
sub-methods it calls can be overridden.
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
from logging import getLogger
from typing import Callable, Dict, List, NamedTuple, Optional, Union

logger = getLogger(__name__)


class NameAndFileName(NamedTuple):
    """Basic named tuple to contain output of a name of a test/testcase and its associated filename.
    """
    name: str
    filename: str


class SummaryWriteOutput(NamedTuple):
    """Named tuple to contain output of a test case's name and filename, and a list of the same for all associated
    test cases.
    """
    test_name_and_filename: NameAndFileName
    l_test_case_names_and_filenames: List[NameAndFileName]


VALUE_TYPE = Union[str, Dict[str, str]]
BUILD_FUNCTION_TYPE = Optional[Callable[[VALUE_TYPE, str], NameAndFileName]]


def hash_any(obj, max_length=None):
    """Hashes any immutable object into a base64 string of a given length.

    Parameters
    ----------
    obj : Any immutable
        The object to be hashed
    max_length : int
        This limits the maximum length of the string to return

    Return
    ------
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


class TestSummaryWriter:
    """Class to handle writing a markdown file containing the summary of a test case. See the documentation of this
    class's __call__ method for further details.
    """

    def __call__(self, value, rootdir):
        """Template method which implements basic writing the summary of output for the test as a whole. Portions of
        this method which call protected methods can be overridden by child classes for customization.

        Parameters
        ----------
        value : str or Dict[str, str]
            The value provided in the .json manifest for this test. This should be either the filename of a tarball
            containing the test results product and associated datafiles, or a dict of keys pointing to multiple
            such files.
        rootdir : str
            The root directory of this project. All filenames provided should be relative to the "data" directory
            within `rootdir`.

        Returns
        -------
        l_test_names_and_filenames : List[SummaryWriteOutput]
            A list of objects, each containing the test name and filename and a list of the same for associated
            tests. If the input `value` is a filename, this will be a single-element list. If the input `value` is
            instead a dict, this will have multiple elements, depending on the number of elements in the dict.

        """
        pass
