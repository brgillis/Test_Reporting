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

import os
import shutil
from logging import getLogger
from typing import Callable, Dict, List, NamedTuple, Optional, Union

from utility.constants import DATA_DIR, PUBLIC_DIR, TEST_REPORTS_SUBDIR
from utility.misc import extract_tarball, hash_any
from utility.product_parsing import parse_xml_product

TMPDIR_MAXLEN = 16

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


class TestSummaryWriter:
    """Class to handle writing a markdown file containing the summary of a test case. See the documentation of this
    class's __call__ method for further details.
    """

    test_name: Optional[str] = None

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
        l_summary_write_output : List[SummaryWriteOutput]
            A list of objects, each containing the test name and filename and a list of the same for associated
            tests. If the input `value` is a filename, this will be a single-element list. If the input `value` is
            instead a dict, this will have multiple elements, depending on the number of elements in the dict.

        """

        # Figure out how to interpret `value` by checking if it's a str or dict, and then iterate over call to
        # process each individual tarball
        l_summary_write_output: List[SummaryWriteOutput]
        if isinstance(value, str):
            l_summary_write_output = self._summarize_results_tarball(value, rootdir, tag=None)
        elif isinstance(value, dict):
            l_summary_write_output = []
            for sub_key, sub_value in value.items():
                l_summary_write_output.append(*self._summarize_results_tarball(sub_value, rootdir, tag=sub_key))
        else:
            raise ValueError("Value in manifest is of unrecognized type.\n"
                             f"Value was: {value}\n"
                             f"Type was: {type(value)}")

        return l_summary_write_output

    def _summarize_results_tarball(self, results_tarball_filename, rootdir, tag=None):
        """Writes summary markdown files for the test results contained in a tarball of the test results product and
        associated data.

        Parameters
        ----------
        results_tarball_filename : str
            The filename of a tarball containing the test results product and associated datafiles
        rootdir : str
        tag : str or None
            If provided, this tag will be appended to the names of all test cases in the returned data, for purposes of
            separately labelling different instances of the same test.

        Returns
        -------
        l_summary_write_output : List[SummaryWriteOutput]
            A list of objects containing the test name and filename and a list of the same for associated tests.
        """

        qualified_tmpdir = self._make_tmpdir(results_tarball_filename, rootdir)

        # We use a try-finally block here to ensure the created tmpdir is removed after use
        try:
            qualified_results_tarball_filename = os.path.join(rootdir, DATA_DIR, results_tarball_filename)
            l_summary_write_output = self._summarize_results_tarball_with_tmpdir(qualified_results_tarball_filename,
                                                                                 qualified_tmpdir,
                                                                                 rootdir,
                                                                                 tag=tag)
        finally:
            shutil.rmtree(qualified_tmpdir)

        return l_summary_write_output

    @staticmethod
    def _make_tmpdir(results_tarball_filename, rootdir):
        """We'll need a temporary directory to extract files into, so create one. To minimize the risk of clashes in
        case of future parallelization, we name it via hashing the filename

        Parameters
        ----------
        results_tarball_filename : str
        rootdir : str

        Returns
        -------
        qualified_tmpdir : str
            The fully-qualified path to a tmpdir created for use by this object

        """

        tmpdir = "tmp_" + hash_any(results_tarball_filename, max_length=TMPDIR_MAXLEN)

        # If this already exists, raise an exception - better to fail then to run into unexpected results from thread
        # clashes
        qualified_tmpdir = os.path.join(rootdir, tmpdir)
        os.makedirs(qualified_tmpdir, exist_ok=False)

        return qualified_tmpdir

    def _summarize_results_tarball_with_tmpdir(self,
                                               qualified_results_tarball_filename,
                                               qualified_tmpdir,
                                               rootdir,
                                               tag=None):
        """Writes summary markdown files for the test results contained in a tarball of the test results product and
        associated data, using a provided tmpdir for work.

        Parameters
        ----------
        qualified_results_tarball_filename : str
            The fully-qualified filename of a tarball containing the test results product and associated datafiles
        qualified_tmpdir : str
            The fully-qualified path to a temporary directory which can be used for this function.
        rootdir : str
        tag : str or None

        Returns
        -------
        l_summary_write_output : List[SummaryWriteOutput]
        """

        extract_tarball(qualified_results_tarball_filename, qualified_tmpdir)

        l_product_filenames = self._find_product_filenames(qualified_tmpdir)
        l_qualified_product_filenames = [os.path.join(qualified_tmpdir, product_filename)
                                         for product_filename in l_product_filenames]

        # Make sure the required subdir exists before we start writing anything
        os.makedirs(os.path.join(rootdir, PUBLIC_DIR, TEST_REPORTS_SUBDIR))

        l_summary_write_output: List[SummaryWriteOutput] = []

        for i, qualified_product_filename in enumerate(l_qualified_product_filenames):

            test_results = parse_xml_product(qualified_product_filename)

            if self.test_name is None:
                test_name = f"TR-{test_results.product_id}"
            else:
                test_name = self.test_name

            if tag is not None:
                test_name += f"-{tag}"

            # If we're processing more than one product, ensure they're all named uniquely
            if len(l_qualified_product_filenames) > 1:
                test_name += f"-{i}"

            test_filename = self._write_test_results_summary(test_results, test_name, rootdir)

            l_summary_write_output.append(SummaryWriteOutput(NameAndFileName(test_name, test_filename), []))

        return l_summary_write_output

    @staticmethod
    def _write_test_results_summary(test_results, test_name, rootdir):
        """Writes out the summary of the test to a .md-format file. If special formatting is desired for an
        individual test, this method can be overridden by child classes.

        Parameters
        ----------
        test_results : TestResults
            Object representing the read-in and parsed .xml product for test results.
        test_name : str
            The name of this test.
        rootdir : str
            The root directory of the project

        Returns
        -------
        test_filename : str
            The filename of the created .md file containing the summary of this test, relative to "public" directory
            within `rootdir`

        """

        test_filename = os.path.join(TEST_REPORTS_SUBDIR, f"{test_name}.md")

        qualified_test_filename = os.path.join(rootdir, PUBLIC_DIR, test_filename)

        with open(qualified_test_filename, "w") as fo:
            fo.write(f"# {test_name}")

        return test_filename

    @staticmethod
    def _find_product_filenames(qualified_tmpdir):
        """Finds the filenames of all .xml products in the provided directory.

        Parameters
        ----------
        qualified_tmpdir : str

        Returns
        -------
        l_product_filenames : List[str]
        """

        l_product_filenames = [fn for fn in os.listdir(qualified_tmpdir) if fn.endswith(".xml")]

        if len(l_product_filenames) == 0:
            raise ValueError("No .xml data products found in tarball.")

        return l_product_filenames
