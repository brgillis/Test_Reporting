"""
:file: utility/test_writing.py

:date: 10/17/2022
:author: Bryan Gillis

This python module provides functionality for writing the test summary markdown files. To allow customization for
individual unit tests, a callable class, TestSummaryWriter, is used, with its call being a template method where
sub-methods it calls can be overridden.

The functionality provided here covers the most general case of reporting results from a SheValidationTestResults
data product where no information is known about the test it's reporting on or the format of information contained
within its SupplementaryInfo, TextFiles, or Figures. It displays all the SupplementaryInfo in one section and all
the Figures in another (at present, nothing is done with TextFiles as no tests yet use them).

For specific tests, the format of this data is likely to be known, and so this is set up to be customizable following
the instructions below.
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
from typing import Callable, Dict, List, NamedTuple, Optional, TYPE_CHECKING, Tuple, Union

from utility.constants import DATA_DIR, IMAGES_SUBDIR, PUBLIC_DIR, TEST_REPORTS_SUBDIR
from utility.misc import TocMarkdownWriter, extract_tarball, hash_any, log_entry_exit
from utility.product_parsing import parse_xml_product

if TYPE_CHECKING:
    from utility.product_parsing import AnalysisResult, RequirementResults, SingleTestResult, TestResults  # noqa F401
    from typing import Sequence, TextIO  # noqa F401

TMPDIR_MAXLEN = 16

DIRECTORY_FILE_EXT = ".txt"
DIRECTORY_FILE_FIGURES_HEADER = "# Figures:"
DIRECTORY_FILE_SEPARATOR = ": "

HEADING_PRODUCT_METADATA = "Product Metadata"
HEADING_TEST_METADATA = "Test Metadata"
HEADING_TEST_CASES = "Test Cases"

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


# Define the expected type for callables used to build test reports, now that the output type from it is defined above
BUILD_CALLABLE_TYPE = Callable[[Union[str, Dict[str, str]], str], List[TestMeta]]


class TestSummaryWriter:
    """Class to handle writing a markdown file containing the summary of a test case. See the documentation of this
    class's `__call__` method for further details of its functionality.

    This can be overridden by child classes to specialize the writing when the format of a SheValidationTestResults
    product is known by following the instructions below.

    Instructions
    ------------

    This class uses a design pattern called the "Template Method". This is used for cases where the same series of
    steps will be undertaken each time, but child classes may wish to handle the details of each step differently.
    This is implemented by using a parent class (defined here), with methods to perform each step of the
    process. Any of these methods can be overridden by child classes to alter the functionality, and so these
    instructions cannot cover all possibilities. Instead, we will provide examples resembling likely use cases.

    Be warned that documentation has a tendency to get out of sync with code, so use the code as the ultimate arbiter,
    not this documentation.

    For any of these cases, you will need to start by defining in a new module a child class of the TestSummaryWriter
    class defined here, which overrides select methods, i.e.:

    ```
    class SpecificTestWriter(TestSummaryWriter):

        test_name = "Specific-Test"

        @staticmethod
        @log_entry_exit(logger)
        def _add_test_case_details(writer, test_case_results):
            '''Specialized implementation of formatting SupplementaryInfo for this test.
            '''
            ...

        ...
    ```

    **Use Case #1: Formatting SupplementaryInfo**

    In the default implementation here, all SupplementaryInfo stored within a product will be printed as-is in a code
    block with no modification. Let's say that for a specific test, you know that there will always be exactly one
    SupplementaryInfo entry, and it will be formatted as:

    ```
    x = <value>
    x_err = <value>
    y = <value>
    y_err = <value>
    ```

    (where each `<value>` is some number), and you wish it to be displayed outside of a code block as:

    ```
    #### Result Values

    x = <value> +/- <value>

    y = <value> +/- <value>
    ```

    To do this, you would find the method here which handles the writing of SupplementaryInfo:
    `_add_test_case_supp_info`. See the documentation of this method for detailed information on it, but to summarize,
    it takes as arguments a `writer`, which is an object used to write sections of the Markdown file with support for
    section headings and auto-generating a Table of Contents, `req`, which is a `RequirementResults` object storing
    the results for this test case (see the definition of that class for details), and `req_i`, which is the index of
    this requirement (which is used to ensure unique labeling of sections for links from the Table of Contents). You
    could then use these to write the child implementation as e.g.:

    ```
    @staticmethod
    def _add_test_case_supp_info(writer, req):
        '''Specialized implementation to write out the x and y values +/- their errors.

        # Add a heading for this section. The depth here is 2 (2 layes deeper than depth 0, which corresponds to the
        # highest level of heading within the body, which is labelled as "##". We don't need any "#" or linebreak at the
        # end when adding the heading. We use the Requirement index in the label here to make sure it's unique.
        writer.add_heading(f"Result Values", depth=2)

        # Here we implement custom parsing of the SupplementaryInfo to get the values we want
        supp_info_str = req.l_supp_info[0].strip()

        l_supp_info_lines = supp_info.split('\n')
        x = l_supp_info_lines[0].split(' = ')[1]
        x_err = l_supp_info_lines[1].split(' = ')[1]
        y = l_supp_info_lines[2].split(' = ')[1]
        y_err = l_supp_info_lines[3].split(' = ')[1]

        # Now we add lines to the writer. `writer.add_line` functions just like `fo.write` where `fo` is a filehandle
        # opened to write or append text. Since we just added a heading, it will automatically have two line breaks
        # after it, so we don't need to handle those ourselves. Remember that this is a MarkDown file, which requires
        # double linebreaks if you wish for things to appear on separate lines.
        writer.add_line(f'x = {x} +/- {x_err}'\n\n)
        writer.add_line(f'y = {y} +/- {y_err}'\n\n)

        # And that's all we need to do here. The writer will be called after everything in the file is added to it. It
        # waits until that point, so it will have all the headings which it will link from the Table of Contents at the
        # top and can write that first.
    ```

    **Use Case #2: Formatting SupplementaryInfo and Figures together**

    One possibility is that multiple figures will be associated with the information contained in a single
    SupplementaryInfo block, and you wish for each of the figures to be displayed alongside the corresponding pieces of
    information. For instance, the SupplementaryInfo might look like:

    ```
    Bin 1:
    slope = <value>
    slope_err = <value>
    intercept = <value>
    intercept_err = <value>

    Bin 2:
    slope = <value>
    slope_err = <value>
    intercept = <value>
    intercept_err = <value>
    ```

    (where each `<value>` is some number), and one figure is provided for each bin.

    In this case, you'll need to override a method a bit higher up in the callstack:
    `_add_test_case_details_and_figures_with_tmpdir`. This handles the writing of both the SupplementaryInfo and Figures
    sections. In the default implementation, it does it sequentially in separate sections, but here you'll want it to be
    done in a single section. The overridden implementation might look something like:

    ```
    def _add_test_case_details_and_figures_with_tmpdir(self,
                                                       writer,
                                                       test_case_results,
                                                       rootdir,
                                                       tmpdir,
                                                       figures_tmpdir):
        writer.add_heading("Results and Figures", depth=0)

        # Dig out the data for each bin from the SupplementaryInfo
        req = test_case_results.l_requirements[0]
        supp_info_str = req.l_supp_info[0].info_value.strip()
        bin_1_str, bin_2_str = supp_info_str.split("\n\n")

        # Get the figure label and filename for each bin
        l_figure_labels_and_filenames = self._prepare_figures(test_case_results.analysis_result, rootdir, tmpdir,
                                                              figures_tmpdir)

        # The object `l_figure_labels_and_filenames` is a list of (label, filename) tuples. In general, there's no
        # guarantee that the labels will be present (non-None) or unique. But in this example, we'll assume that we
        # do have such a guarantee, and that the two labels will be "bin-1" and "bin-2". We can then better sort this
        # into a dict:
        d_figure_filenames = {figure_label: figure_filename for (figure_label, figure_filename) in
                              l_figure_labels_and_filenames}

        # Write info for each bin
        for bin_i, bin_str in enumerate((bin_1_str, bin_2_str)):

            filename = d_figure_filenames[f"bin-{bin_i + 1}"]

            # Copy the figure to the appropriate directory and get the relative filename for it using the provided
            # method
            relative_figure_filename = self._move_figure_to_public(filename, rootdir, figures_tmpdir)

            # Add a heading for this bin's subsection, at a depth 1 greater than that of this section
            bin_label = f"Bin {bin_i}"
            writer.add_heading(bin_label, depth=1)

            # Add a link to the figure
            writer.add_line(f"![{bin_label}]({relative_figure_filename})\n\n")

            # Get the slope and intercept info out of the info string for this specific bin by properly parsing it
            l_bin_info_lines = bin_str.split("\n")
            slope = l_bin_info_lines[1].split(" = ")[1]
            slope_err = l_bin_info_lines[2].split(" = ")[1]
            intercept = l_bin_info_lines[3].split(" = ")[1]
            intercept_err = l_bin_info_lines[4].split(" = ")[1]

            # And finally, add lines for the slope and intercept info, still in the same section as the associated
            # figure
            writer.add_line(f"slope = {slope} +/- {slope_err}\n\n")
            writer.add_line(f"intercept = {intercept} +/- {intercept_err}\n\n")
    ```
    """

    # Class attribute definitions - these can be overridden by child classes to specify the value without needing to
    # use the `__init__`
    test_name: Optional[str] = None

    @log_entry_exit(logger)
    def __init__(self, test_name: Optional[str] = None):
        """Initializer for TestSummaryWriter, which allows specifying the test name.

        Parameters
        ----------
        test_name : str or None
            The name of the test, which will be used for titling its page in the output. If not provided, will be set
            to the `test_name` class attribute.
        """
        self.test_name = test_name if test_name is not None else self.test_name

    @log_entry_exit(logger)
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

    @log_entry_exit(logger)
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
    @log_entry_exit(logger)
    def _make_tmpdir(hashable, rootdir):
        """We'll need a temporary directory to extract files into, so create one. Some unique hashable object must be
        provided, whose hash will be used to generate a presumably-unique directory name.

        Parameters
        ----------
        hashable : Any
        rootdir : str

        Returns
        -------
        qualified_tmpdir : str
            The fully-qualified path to a tmpdir created for use by this object
        """

        tmpdir = "tmp_" + hash_any(hashable, max_length=TMPDIR_MAXLEN)

        # If this already exists, raise an exception - better to fail then to run into unexpected results from thread
        # clashes
        qualified_tmpdir = os.path.join(rootdir, tmpdir)
        os.makedirs(qualified_tmpdir, exist_ok=False)

        return qualified_tmpdir

    @log_entry_exit(logger)
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
        os.makedirs(os.path.join(rootdir, PUBLIC_DIR, TEST_REPORTS_SUBDIR), exist_ok=True)

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

            logger.info("Building report for test %s.", test_name)

            # We write the pages for the test cases first, so we know about and can link to them from the test
            # summary page
            l_test_case_meta = self._write_all_test_case_results(test_results=test_results,
                                                                 test_name_tail=test_name_tail,
                                                                 rootdir=rootdir,
                                                                 tmpdir=qualified_tmpdir)

            test_filename = self._write_test_results_summary(test_results=test_results,
                                                             test_name=test_name,
                                                             l_test_case_meta=l_test_case_meta,
                                                             rootdir=rootdir)

            num_passed, num_failed = self._calc_num_passed_failed(l_test_case_meta)
            l_test_meta.append(TestMeta(name=test_name,
                                        filename=test_filename,
                                        l_test_case_meta=l_test_case_meta,
                                        num_passed=num_passed,
                                        num_failed=num_failed))

        return l_test_meta

    @staticmethod
    @log_entry_exit(logger)
    def _calc_num_passed_failed(l_test_case_meta):
        """Calculates the number of test cases which have passed and failed from the provided list of TestCaseMeta.

        Parameters
        ----------
        l_test_case_meta : Sequence[TestCaseMeta]

        Returns
        -------
        num_passed : int
        num_failed : int
        """

        num_passed = sum([1 for x in l_test_case_meta if x.passed])
        num_failed = len(l_test_case_meta) - num_passed

        return num_passed, num_failed

    @staticmethod
    @log_entry_exit(logger)
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

    @log_entry_exit(logger)
    def _write_all_test_case_results(self, test_results, test_name_tail, rootdir, tmpdir):
        """Writes out the results of all test cases to a .md-format file.

        Parameters
        ----------
        test_results : TestResults
            Object representing the read-in and parsed .xml product for test results.
        test_name_tail : str
            The extra "tail" added to the end of the test name, which will also be added to the end of all test case
            names.
        rootdir : str
        tmpdir : str

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
            self._write_individual_test_case_results(test_case_results=test_case_results,
                                                     test_case_name=test_case_name,
                                                     test_case_filename=test_case_filename,
                                                     rootdir=rootdir,
                                                     tmpdir=tmpdir)

        return l_test_case_names_and_filenames

    @log_entry_exit(logger)
    def _write_individual_test_case_results(self,
                                            test_case_results,
                                            test_case_name,
                                            test_case_filename,
                                            rootdir,
                                            tmpdir):
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
        tmpdir : str
        """

        qualified_test_case_filename = os.path.join(rootdir, PUBLIC_DIR, test_case_filename)

        logger.info("Writing results for test case %s from %s.", test_case_name, qualified_test_case_filename)

        # Ensure the folder for this exists
        os.makedirs(os.path.split(qualified_test_case_filename)[0], exist_ok=True)

        writer = TocMarkdownWriter(test_case_name)

        self._add_test_case_meta(writer, test_case_results)

        self._add_test_case_details_and_figures(test_case_results, writer, rootdir, tmpdir)

        with open(qualified_test_case_filename, "w") as fo:
            writer.write(fo)

    @staticmethod
    @log_entry_exit(logger)
    def _add_test_case_meta(writer, test_case_results):
        """Adds lines for the metadata associated with an individual test case to a MarkdownWriter.

        Parameters
        ----------
        writer : TocMarkdownWriter
            The writer object set up to write a markdown report on a test case
        test_case_results : SingleTestResult
        """

        writer.add_heading("General Information", depth=0)
        writer.add_line(f"**Test Case ID:** {test_case_results.test_id}\n\n")
        writer.add_line(f"**Description:** {test_case_results.test_description}\n\n")
        writer.add_line(f"**Result:** {test_case_results.global_result}\n\n")
        if test_case_results.analysis_result.ana_comment is not None:
            writer.add_line(f"**Comments:** {test_case_results.analysis_result.ana_comment}\n\n")

    @log_entry_exit(logger)
    def _add_test_case_details_and_figures(self, test_case_results, writer, rootdir, tmpdir):
        """Adds lines for the supplementary info associated with an individual test case to a MarkdownWriter,
        prepares figures, and also adds lines for them.

        Parameters
        ----------
        writer : TocMarkdownWriter
        test_case_results : SingleTestResult
        rootdir : str
        tmpdir : str
        """

        # Make a new tmpdir within the existing tmpdir for this batch of figures and textfiles (to avoid name clashes
        # with other test cases)
        figures_tmpdir = self._make_tmpdir(test_case_results, tmpdir)

        try:
            self._add_test_case_details_and_figures_with_tmpdir(writer, test_case_results, rootdir, tmpdir,
                                                                figures_tmpdir)
        finally:
            shutil.rmtree(figures_tmpdir)

    @log_entry_exit(logger)
    def _add_test_case_details_and_figures_with_tmpdir(self,
                                                       writer,
                                                       test_case_results,
                                                       rootdir,
                                                       tmpdir,
                                                       figures_tmpdir):
        """Adds lines for the supplementary info associated with an individual test case to a MarkdownWriter,
        prepares figures, and also adds lines for them, after a temporary directory has been created to store figures
        data.

        In the default implementation, this method performs these tasks sequentially and separately since nothing
        can be assumed about how the supplementary info and figures relate. In child classes where the relationship is
        know, this may be overridden to handle the two together if desired.

        Parameters
        ----------
        writer : TocMarkdownWriter
        test_case_results : SingleTestResult
        rootdir : str
        tmpdir : str
            The fully-qualified path to the temporary directory containing all data for this test.
        figures_tmpdir : str
            The fully-qualified path to the temporary directory set up to contain figures data for this test case.
        """
        self._add_test_case_details(writer, test_case_results)
        self._add_test_case_figures(writer=writer,
                                    ana_result=test_case_results.analysis_result,
                                    rootdir=rootdir,
                                    tmpdir=tmpdir,
                                    figures_tmpdir=figures_tmpdir)

    @log_entry_exit(logger)
    def _add_test_case_details(self, writer, test_case_results):
        """Adds a section for detailed results of an individual test case to a MarkdownWriter.

        Parameters
        ----------
        writer : TocMarkdownWriter
        test_case_results : SingleTestResult
        """

        # We can't guarantee that supplementary info keys will be unique between different requirements,
        # so to ensure we have unique links for each, we keep a counter and add it to the name of each
        writer.add_heading("Detailed Results", depth=0)
        for req_i, req in enumerate(test_case_results.l_requirements):
            writer.add_heading("Requirement", depth=1)
            writer.add_line(f"**Measured Parameter**: {req.meas_value.parameter}\n\n")
            writer.add_line(f"**Measured Value**: {req.meas_value.value}\n\n")
            if req.req_comment is not None:
                writer.add_line(f"**Comments**: {req.req_comment}\n\n")
            self._add_test_case_supp_info(writer, req)

    @staticmethod
    def _add_test_case_supp_info(writer, req):
        """Adds lines for the supplementary info associated with an individual test case to a MarkdownWriter.

        Parameters
        ----------
        writer : TocMarkdownWriter
        req : RequirementResults
            The object containing the results for a specific requirement.
        """

        for supp_info_i, supp_info in enumerate(req.l_supp_info):
            writer.add_heading(f"{supp_info.info_key}", depth=2)
            writer.add_line(f"{supp_info.info_description}\n\n")
            writer.add_line("```\n")

            # Trim excess line breaks from the supplementary info's beginning and end
            supp_info_str = supp_info.info_value.strip()

            writer.add_line(supp_info_str)

            writer.add_line("\n```\n\n")

    @log_entry_exit(logger)
    def _add_test_case_figures(self, writer, ana_result, rootdir, tmpdir, figures_tmpdir):
        """Prepares figures and adds lines for them to a MarkdownWriter, after a new temporary directory has been
        created to store extracted files in.

        Parameters
        ----------
        writer : TocMarkdownWriter
        ana_result : AnalysisResult
            The AnalysisResult object containing the filenames of textfiles and figures tarballs for this test case.
        rootdir : str
        tmpdir : str
            The fully-qualified path to the temporary directory containing all data for this test.
        figures_tmpdir : str
            The fully-qualified path to the temporary directory set up to contain figures data for this test case.
        """

        writer.add_heading("Figures", depth=0)

        l_figure_labels_and_filenames = self._prepare_figures(ana_result, rootdir, tmpdir, figures_tmpdir)

        # Check we prepared successfully; if not, return, so we don't hit any further errors
        if not l_figure_labels_and_filenames:
            writer.add_line("N/A\n\n")
            return

        # Add a subsection for each figure to the writer
        for i, (label, filename) in enumerate(l_figure_labels_and_filenames):

            # Make a label if we don't have one
            if label is None:
                label = f"Figure #{i}"

            relative_figure_filename = self._move_figure_to_public(filename, rootdir, figures_tmpdir)

            writer.add_heading(label, depth=1)
            writer.add_line(f"![{label}]({relative_figure_filename})\n\n")

    @staticmethod
    def _move_figure_to_public(filename, rootdir, figures_tmpdir):
        """Move a figure to the appropriate directory and return the relative filename for it.

        Parameters
        ----------
        filename : str
            The filename of the figure relative to the `figures_tmpdir`
        rootdir : str
        figures_tmpdir : str
            The fully-qualified path to the tmpdir created to store unpacked figures.

        Returns
        -------
        relative_figure_filename : str or None
            The path to the moved figure relative to where test reports are stored. In case of an error where the
            file wasn't present, the error will be logged and None will be returned instead.
        """

        qualified_src_filename = os.path.join(figures_tmpdir, filename)
        qualified_dest_filename = os.path.join(rootdir, PUBLIC_DIR, IMAGES_SUBDIR, filename)

        # Check for file existence
        if not os.path.isfile(qualified_src_filename):
            # Source doesn't exist. If destination does, then there's no issue - assumedly it's already been moved
            # for another page, and so we don't need to move it again. If destination doesn't exist, then we have an
            # error.
            if not os.path.isfile(qualified_dest_filename):
                logger.error(f"Expected figure {filename} does not exist.")
                return None
        else:
            shutil.move(qualified_src_filename, qualified_dest_filename)

        # Return the path to the moved figure file, relative to where test reports will be stored
        return f"../{IMAGES_SUBDIR}/{filename}"

    def _prepare_figures(self, ana_result, rootdir, tmpdir, figures_tmpdir):
        """Performs standard steps to prepare figures - unpacking them, reading the directory file, and setting up
        expected output directory.

        Parameters
        ----------
        ana_result : AnalysisResult
            Object containing information about the textfiles and figures for a given test case.
        rootdir : str
        tmpdir : str
            The tmpdir which was used to extract the full tarball of the product and associated data.
        figures_tmpdir : str
            The tmpdir to be used to extract the textfiles and figures in their respective tarballs.

        Returns
        -------
        l_figure_labels_and_filenames : List[Tuple[str or None,str]] or None
            A list of (label,filename) tuples which were read in from the directory file. If expected files are not
            present, None will be returned instead.
        """

        # Check if any figures are present
        if ana_result.figures_tarball is None or ana_result.textfiles_tarball is None:
            # None present, but this might be expected, so just log at debug level
            logger.debug("No figures associated with this test case.")
            return None

        # Extract the textfiles and figures tarballs
        qualified_figures_tarball_filename = os.path.join(tmpdir, ana_result.figures_tarball)
        qualified_textfiles_tarball_filename = os.path.join(tmpdir, ana_result.textfiles_tarball)

        for qualified_tarball_filename in (qualified_figures_tarball_filename, qualified_textfiles_tarball_filename):
            if not os.path.isfile(qualified_tarball_filename):
                logger.error("Tarball %s expected but not present.", qualified_tarball_filename)
                return None

        extract_tarball(qualified_figures_tarball_filename, figures_tmpdir)
        extract_tarball(qualified_textfiles_tarball_filename, figures_tmpdir)

        # Find the "directory" file which should have been in the tarball, and get the labels and filenames of
        # figures from it
        qualified_directory_filename = self.find_directory_filename(figures_tmpdir)
        l_figure_labels_and_filenames = self.read_figure_labels_and_filenames(qualified_directory_filename)

        # Make sure a data subdir exists in the images dir
        os.makedirs(os.path.join(rootdir, PUBLIC_DIR, IMAGES_SUBDIR, DATA_DIR), exist_ok=True)

        return l_figure_labels_and_filenames

    @staticmethod
    @log_entry_exit(logger)
    def find_directory_filename(figures_tmpdir):
        """Searches through a directory to find a possible directory file (which contains labels and filenames of
        figures).

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
            if filename.endswith(DIRECTORY_FILE_EXT):
                l_possible_directory_filenames.append(filename)

        # Check we have exactly one possibility, otherwise raise an exception
        if len(l_possible_directory_filenames) == 1:
            qualified_directory_filename = os.path.join(figures_tmpdir, l_possible_directory_filenames[0])
            logger.info("Found directory file for this test case: %s", qualified_directory_filename)
            return qualified_directory_filename
        elif len(l_possible_directory_filenames) == 0:
            raise FileNotFoundError(f"No identifiable directory file found in directory {figures_tmpdir}.")
        else:
            raise ValueError(f"Multiple possible directory files found in directory {figures_tmpdir}: "
                             f"{l_possible_directory_filenames}")

    @staticmethod
    @log_entry_exit(logger)
    def read_figure_labels_and_filenames(qualified_directory_filename):
        """Reads a directory file, and returns a list of figure labels and filenames. Note that any figure label
        might be None if it's not supplied in the directory file.

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
                if directory_line == DIRECTORY_FILE_FIGURES_HEADER:
                    figures_section_started = True
                continue

            # If we get here, we're in the figures section
            figure_label: Optional[str] = None
            figure_filename: str
            if DIRECTORY_FILE_SEPARATOR in directory_line:
                figure_label, figure_filename = directory_line.split(DIRECTORY_FILE_SEPARATOR)
            else:
                figure_filename = directory_line

            if figure_filename is not None and figure_filename != "None":
                l_figure_labels_and_filenames.append((figure_label, figure_filename))

        return l_figure_labels_and_filenames

    @log_entry_exit(logger)
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

        logger.info("Writing test results summary to %s", qualified_test_filename)

        writer = TocMarkdownWriter(test_name)

        self._write_product_metadata(test_results, writer)
        self._write_test_metadata(test_results, writer)
        self._write_test_case_table(test_results, l_test_case_meta, writer)

        # Ensure the folder for this exists
        os.makedirs(os.path.split(qualified_test_filename)[0], exist_ok=True)

        with open(qualified_test_filename, "w") as fo:
            writer.write(fo)

        return test_filename

    @staticmethod
    @log_entry_exit(logger)
    def _write_product_metadata(test_results, writer):
        """Writes metadata related to the test's data product to an open filehandle

        Parameters
        ----------
        test_results : TestResults
        writer : TocMarkdownWriter
            A writer to handle storing heading and lines we wish to be written out to a file
        """

        writer.add_heading(HEADING_PRODUCT_METADATA, depth=0)

        writer.add_line(f"**Product ID:** {test_results.product_id}\n\n")
        writer.add_line(f"**Dataset Release:** {test_results.dataset_release}\n\n")
        writer.add_line(f"**Plan ID:** {test_results.plan_id}\n\n")
        writer.add_line(f"**PPO ID:** {test_results.ppo_id}\n\n")
        writer.add_line(f"**Pipeline Definition ID:** {test_results.pipeline_definition_id}\n\n")
        writer.add_line(f"**Source Pipeline:** {test_results.source_pipeline}\n\n")

        t = test_results.creation_date
        month_name = t.strftime("%b")
        writer.add_line(f"**Creation Date and Time:** {t.day} {month_name}, {t.year} at {t.time()}\n\n")

    @staticmethod
    @log_entry_exit(logger)
    def _write_test_metadata(test_results, writer):
        """Writes metadata related to the test itself to an open filehandle

        Parameters
        ----------
        test_results : TestResults
        writer : TocMarkdownWriter
        """

        writer.add_heading(HEADING_TEST_METADATA, depth=0)

        if test_results.exp_product_id is not None:
            writer.add_line(f"**Exposure Product ID:** {test_results.exp_product_id}\n\n")
        if test_results.obs_id is not None:
            writer.add_line(f"**Observation ID:** {test_results.obs_id}\n\n")
        if test_results.pnt_id is not None:
            writer.add_line(f"**Pointing ID:** {test_results.pnt_id}\n\n")
        if test_results.n_exp is not None:
            writer.add_line(f"**Number of Exposures:** {test_results.n_exp}\n\n")
        if test_results.tile_id is not None:
            writer.add_line(f"**Tile ID:** {test_results.tile_id}\n\n")
        if test_results.obs_mode is not None:
            writer.add_line(f"**Observation Mode:** {test_results.obs_mode}\n\n")

    @log_entry_exit(logger)
    def _write_test_case_table(self, test_results, l_test_case_meta, writer):
        """Writes a table containing test case information and links to their pages to an open filehandle.

        Parameters
        ----------
        test_results : TestResults
        l_test_case_meta : Sequence[TestCaseMeta]
        writer : TocMarkdownWriter
        """

        writer.add_heading(HEADING_TEST_CASES, depth=0)

        num_passed, num_failed = self._calc_num_passed_failed(l_test_case_meta)

        writer.add_line(f"Number of Test Cases passed: {num_passed}\n\n")
        writer.add_line(f"Number of Test Cases failed: {num_failed}\n\n")

        writer.add_line("| **Test Case** | **Result** |\n")
        writer.add_line("| :------------ | :--------- |\n")

        for (test_case_meta, test_case_results) in zip(l_test_case_meta,
                                                       test_results.l_test_results):
            test_case_name = test_case_meta.name

            # Change suffix of filename from .md to .html and remove the beginning "TR/", since this will be linked from
            # a file already in that folder
            html_filename = f"{test_case_meta.filename[3:-3]}.html"

            test_line = f"| [{test_case_name}]({html_filename}) | {test_case_results.global_result} |\n"
            writer.add_line(test_line)
