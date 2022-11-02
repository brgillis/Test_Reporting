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
from typing import Callable, Dict, List, NamedTuple, Optional, TYPE_CHECKING, Union

from utility.constants import DATA_DIR, PUBLIC_DIR, TEST_REPORTS_SUBDIR
from utility.misc import extract_tarball, hash_any
from utility.product_parsing import parse_xml_product

if TYPE_CHECKING:
    from utility.product_parsing import SingleTestResult, TestResults  # noqa F401
    from typing import Sequence, TextIO  # noqa F401

TMPDIR_MAXLEN = 16

logger = getLogger(__name__)


class TestCaseMeta(NamedTuple):
    """Named tuple to contain output of a name of a test/testcase and its associated filename, plus optionally
    whether or not it passed.
    """
    name: str
    filename: str
    passed: Optional[bool] = None


class TestMeta(NamedTuple):
    """Named tuple to contain output of a test case's name and filename, and a list of the same for all associated
    test cases.
    """
    name: str
    filename: str
    l_test_case_meta: Sequence[TestCaseMeta]
    num_passed: int = -1
    num_failed: int = -1


VALUE_TYPE = Union[str, Dict[str, str]]
BUILD_FUNCTION_TYPE = Optional[Callable[[VALUE_TYPE, str], List[TestMeta]]]


class MarkdownWriter:
    """Class to help with writing more-complicated Markdown files which include a Table of Contents.
    """

    def __init__(self, title: str):
        self.title = title
        self._l_lines: List[str] = []
        self._l_toc_lines: List[str] = []

    def add_line(self, line: str):
        """Add a standard line to be written as part of the body text of the file.
        """
        self._l_lines.append(line)

    def add_heading(self, heading: str, depth: int = 0, label: Optional[str] = None):
        """Add a heading line to be written, which should also be linked from the table-of contents.
        """

        # Trim any ending newlines, and beginning #s and spaces
        while heading.endswith("\n"):
            heading = heading[:-1]
        while heading.startswith("#"):
            heading = heading[1:]
        heading = heading.strip()

        if label is None:
            label = heading.lower().replace(" ", "-")

        self._l_lines.append("#" * (depth + 2) + f" {heading} <a id=\"{label}\"></a>\n\n")

        self._l_toc_lines.append("  " * depth + f"1. [{heading}](#{label})\n")

    def write(self, fo: TextIO):
        """Writes out the TOC and all lines.
        """

        fo.write(f"# {self.title}\n\n")

        fo.write(f"## Table of Contents\n\n")

        for line in self._l_toc_lines:
            fo.write(line)

        fo.write("\n")

        for line in self._l_lines:
            fo.write(line)


class TestSummaryWriter:
    """Class to handle writing a markdown file containing the summary of a test case. See the documentation of this
    class's __call__ method for further details.
    """

    test_name: Optional[str] = None

    def __init__(self, test_name: Optional[str] = None):
        """Initializer for TestSummaryWriter, which allows specifying the test name.

        Parameters
        ----------
        test_name : str or None
            The name of the test, which will be used for titling its page in the output.
        """
        self.test_name = test_name if test_name is not None else self.test_name

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
        l_test_meta : List[TestMeta]
            A list of objects, each containing the test name and filename and a list of the same for associated
            tests. If the input `value` is a filename, this will be a single-element list. If the input `value` is
            instead a dict, this will have multiple elements, depending on the number of elements in the dict.

        """

        # Figure out how to interpret `value` by checking if it's a str or dict, and then iterate over call to
        # process each individual tarball
        l_test_meta: List[TestMeta]
        if isinstance(value, str):
            l_test_meta = self._summarize_results_tarball(value, rootdir, tag=None)
        elif isinstance(value, dict):
            l_test_meta = []
            for sub_key, sub_value in value.items():
                l_test_meta += self._summarize_results_tarball(sub_value, rootdir, tag=sub_key)
        else:
            raise ValueError("Value in manifest is of unrecognized type.\n"
                             f"Value was: {value}\n"
                             f"Type was: {type(value)}")

        return l_test_meta

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
        l_test_meta : List[TestMeta]
            A list of objects containing the test name and filename and a list of the same for associated tests.
        """

        # Check for no input
        if results_tarball_filename is None:
            return []

        qualified_tmpdir = self._make_tmpdir(results_tarball_filename, rootdir)

        # We use a try-finally block here to ensure the created tmpdir is removed after use
        try:
            qualified_results_tarball_filename = os.path.join(rootdir, DATA_DIR, results_tarball_filename)
            l_test_meta = self._summarize_results_tarball_with_tmpdir(qualified_results_tarball_filename,
                                                                      qualified_tmpdir,
                                                                      rootdir,
                                                                      tag=tag)
        finally:
            shutil.rmtree(qualified_tmpdir)

        return l_test_meta

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
        l_test_meta : List[TestMeta]
        """

        extract_tarball(qualified_results_tarball_filename, qualified_tmpdir)

        l_product_filenames = self._find_product_filenames(qualified_tmpdir)
        l_qualified_product_filenames = [os.path.join(qualified_tmpdir, product_filename)
                                         for product_filename in l_product_filenames]

        # Make sure the required subdir exists before we start writing anything
        os.makedirs(os.path.join(rootdir, PUBLIC_DIR, TEST_REPORTS_SUBDIR))

        l_test_meta: List[TestMeta] = []

        for i, qualified_product_filename in enumerate(l_qualified_product_filenames):

            test_results = parse_xml_product(qualified_product_filename)

            test_name_tail = ""

            if tag is not None:
                test_name_tail += f"-{tag}"

            # If we're processing more than one product, ensure they're all named uniquely
            if len(l_qualified_product_filenames) > 1:
                test_name_tail += f"-{i}"

            if self.test_name is None:
                test_name = f"TR-{test_results.product_id}{test_name_tail}"
            else:
                test_name = f"{self.test_name}{test_name_tail}"

            # We write the pages for the test cases first, so we know about and can link to them from the test
            # summary page
            l_test_case_meta = self._write_all_test_case_results(test_results, test_name_tail, rootdir)

            # Calculate the number of test cases which passed and the number which failed
            num_passed = sum([1 for x in l_test_case_meta if x.passed])
            num_failed = len(l_test_case_meta) - num_passed

            test_filename = self._write_test_results_summary(test_results=test_results,
                                                             test_name=test_name,
                                                             l_test_case_meta=l_test_case_meta,
                                                             rootdir=rootdir)

            l_test_meta.append(TestMeta(name=test_name,
                                        filename=test_filename,
                                        l_test_case_meta=l_test_case_meta,
                                        num_passed=num_passed,
                                        num_failed=num_failed))

        return l_test_meta

    @staticmethod
    def _find_product_filenames(qualified_tmpdir):
        """Finds the filenames of all .xml products in the provided directory. If certain .xml files should be
        ignored for a given test, this method can be overridden to handle that.

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

    def _write_all_test_case_results(self, test_results, test_name_tail, rootdir):
        """Writes out the results of all test cases to a .md-format file.

        Parameters
        ----------
        test_results : TestResults
            Object representing the read-in and parsed .xml product for test results.
        test_name_tail : str
            The extra "tail" added to the end of the test name, which will also be added to the end of all test case
            names.
        rootdir : str

        Returns
        -------
        l_test_case_names_and_filenames : Sequence[TestCaseMeta]
            The names and generated file names of each test case associated with this test.
        """

        # We handle naming the test cases in this method, so we can check for the presence of duplicates
        d_test_name_instances: Dict[str, int] = {}
        l_test_case_names_and_filenames: List[TestCaseMeta] = []
        for test_case_results in test_results.l_test_results:

            test_case_id = test_case_results.test_id
            if test_case_id in d_test_name_instances:
                d_test_name_instances[test_case_id] += 1
                test_case_name = f"{test_case_id}-{d_test_name_instances[test_case_id]}{test_name_tail}"
            else:
                d_test_name_instances[test_case_id] = 1
                test_case_name = f"{test_case_id}{test_name_tail}"

            test_case_filename = os.path.join(TEST_REPORTS_SUBDIR, f"{test_case_name}.md")

            l_test_case_names_and_filenames.append(TestCaseMeta(name=test_case_name,
                                                                filename=test_case_filename,
                                                                passed=(test_case_results.global_result ==
                                                                        "PASSED")))

            # Now we defer to a sub-method to write the results, so the formatting in that bit can be easily overridden
            self._write_individual_test_case_results(test_case_results, test_case_name, test_case_filename, rootdir)

        return l_test_case_names_and_filenames

    def _write_individual_test_case_results(self, test_case_results, test_case_name, test_case_filename, rootdir):
        """Writes out the results of all test cases to a .md-format file. If special formatting is desired for an
        individual test case, this method can be overridden.

        Parameters
        ----------
        test_case_results : SingleTestResult
            Object representing the element of the read-in and parsed .xml product for test results which contains
            the results for an individual test case.
        test_case_name : str
            The name of this individual test case
        test_case_filename : str
            The desired filename for the report on this test case. This should be relative to the "public" directory
            in the rootdir and unique for each test case.
        rootdir : str
        """

        qualified_test_case_filename = os.path.join(rootdir, PUBLIC_DIR, test_case_filename)

        # Ensure the folder for this exists
        os.makedirs(os.path.split(qualified_test_case_filename)[0], exist_ok=True)

        writer = MarkdownWriter(test_case_name)

        writer.add_heading("General Information", depth=0)
        writer.add_line(f"**Test Case ID:** {test_case_results.test_id}\n\n")
        writer.add_line(f"**Description:** {test_case_results.test_description}\n\n")
        writer.add_line(f"**Result:** {test_case_results.global_result}\n\n")
        if test_case_results.analysis_result.ana_comment is not None:
            writer.add_line(f"**Comments:** {test_case_results.analysis_result.ana_comment}\n\n")

        # We can't guarantee that supplementary info keys will be unique between different requirements,
        # so to ensure we have unique links for each, we keep a counter and add it to the name of each
        supp_info_counter = 0

        writer.add_heading("Detailed Results", depth=0)
        for req in test_case_results.l_requirements:
            writer.add_heading("Requirement", depth=1)
            writer.add_line(f"**Measured Parameter**: {req.meas_value.parameter}\n\n")
            writer.add_line(f"**Measured Value**: {req.meas_value.value}\n\n")
            if req.req_comment is not None:
                writer.add_line(f"**Comments**: {req.req_comment}\n\n")
            for supp_info in req.l_supp_info:
                writer.add_heading(f"{supp_info.info_key}", depth=2, label=f"si-{supp_info_counter}")
                supp_info_counter += 1
                writer.add_line(f"{supp_info.info_description}\n\n")
                writer.add_line("```\n")
                writer.add_line(supp_info.info_value)
                writer.add_line("```\n\n")

        writer.add_line(f"## Figures\n\n")
        writer.add_line("(Automatic generation of this section is not yet ready)")

        with open(qualified_test_case_filename, "w") as fo:
            writer.write(fo)

    def _write_test_results_summary(self, test_results, test_name, l_test_case_meta, rootdir):
        """Writes out the summary of the test to a .md-format file. If special formatting is desired for an
        individual test, this method or the methods it calls can be overridden by child classes.

        Parameters
        ----------
        test_results : TestResults
        test_name : str
            The name of this test.
        l_test_case_meta : Sequence[TestCaseMeta]
            The names and file names of each test case associated with this test.
        rootdir : str

        Returns
        -------
        test_filename : str
            The filename of the created .md file containing the summary of this test, relative to "public" directory
            within `rootdir`

        """

        test_filename = os.path.join(TEST_REPORTS_SUBDIR, f"{test_name}.md")

        qualified_test_filename = os.path.join(rootdir, PUBLIC_DIR, test_filename)

        # Ensure the folder for this exists
        os.makedirs(os.path.split(qualified_test_filename)[0], exist_ok=True)

        with open(qualified_test_filename, "w") as fo:
            fo.write(f"# {test_name}\n\n")

            self._write_product_metadata(test_results, fo)

            fo.write("\n")

            self._write_test_metadata(test_results, fo)

            fo.write("\n")

            self._write_test_case_table(test_results, l_test_case_meta, fo)

        return test_filename

    @staticmethod
    def _write_product_metadata(test_results, fo):
        """Writes metadata related to the test's data product to an open filehandle

        Parameters
        ----------
        test_results : TestResults
        fo : TextIO
            A filehandle for the desired file, opened for writing text output
        """

        fo.write(f"## Product Metadata\n\n")

        fo.write(f"**Product ID:** {test_results.product_id}\n\n")
        fo.write(f"**Dataset Release:** {test_results.dataset_release}\n\n")
        fo.write(f"**Plan ID:** {test_results.plan_id}\n\n")
        fo.write(f"**PPO ID:** {test_results.ppo_id}\n\n")
        fo.write(f"**Pipeline Definition ID:** {test_results.pipeline_definition_id}\n\n")
        fo.write(f"**Source Pipeline:** {test_results.source_pipeline}\n\n")

        t = test_results.creation_date
        month_name = t.strftime("%b")
        fo.write(f"**Creation Date and Time:** {t.day} {month_name}, {t.year} at {t.time()}\n\n")

    @staticmethod
    def _write_test_metadata(test_results, fo):
        """Writes metadata related to the test itself to an open filehandle

        Parameters
        ----------
        test_results : TestResults
        fo : TextIO
        """

        fo.write("## Test Metadata\n\n")

        if test_results.exp_product_id is not None:
            fo.write(f"**Exposure Product ID:** {test_results.exp_product_id}\n\n")
        if test_results.obs_id is not None:
            fo.write(f"**Observation ID:** {test_results.obs_id}\n\n")
        if test_results.pnt_id is not None:
            fo.write(f"**Pointing ID:** {test_results.pnt_id}\n\n")
        if test_results.n_exp is not None:
            fo.write(f"**Number of Exposures:** {test_results.n_exp}\n\n")
        if test_results.tile_id is not None:
            fo.write(f"**Tile ID:** {test_results.tile_id}\n\n")
        if test_results.obs_mode is not None:
            fo.write(f"**Observation Mode:** {test_results.obs_mode}\n\n")

    @staticmethod
    def _write_test_case_table(test_results, l_test_case_meta, fo):
        """Writes a table containing test case information and links to their pages to an open filehandle.

        Parameters
        ----------
        test_results : TestResults
        l_test_case_meta : Sequence[TestCaseMeta]
        fo : TextIO
        """

        fo.write("## Test Cases\n\n")

        fo.write("| **Test Case** | **Result** |\n")
        fo.write("| :------------ | :--------- |\n")

        for (test_case_meta, test_case_results) in zip(l_test_case_meta,
                                                       test_results.l_test_results):
            test_case_name = test_case_meta.name

            # Change suffix of filename from .md to .html and remove the beginning "TR/", since this will be linked from
            # a file already in that folder
            html_filename = f"{test_case_meta.filename[3:-3]}.html"

            test_line = f"| [{test_case_name}]({html_filename}) | {test_case_results.global_result} |\n"
            fo.write(test_line)
