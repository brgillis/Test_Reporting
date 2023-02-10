"""
:file: Test_Reporting/utility/report_writing.py

:date: 10/17/2022
:author: Bryan Gillis

This python module provides functionality for writing the test summary markdown files. To allow customization for
individual unit tests, a callable class, ReportSummaryWriter, is used, with its call being a template method where
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
from enum import Enum
from logging import getLogger
from typing import Callable, Dict, List, NamedTuple, Optional, Sequence, TYPE_CHECKING, Tuple, Union

from astropy.io.registry import IORegistryError
from astropy.table import Table

from Test_Reporting.utility.constants import DATA_DIR, IMAGES_SUBDIR, PUBLIC_DIR, TEST_REPORTS_SUBDIR
from Test_Reporting.utility.misc import (TocMarkdownWriter, extract_tarball, get_data_filename, get_qualified_path,
                                         hash_any, is_valid_tarball_filename, is_valid_xml_filename, log_entry_exit, )
from Test_Reporting.utility.product_parsing import parse_xml_product

if TYPE_CHECKING:
    from typing import TextIO  # noqa F401
    from Test_Reporting.utility.product_parsing import (AnalysisResult, RequirementResults,  # noqa F401
                                                        SingleTestResult, TestResults, )  # noqa F401

TMPDIR_MAXLEN = 16

DIRECTORY_FILE_EXT = ".txt"
DIRECTORY_FILE_TEXTFILES_HEADER = "# Textfiles:"
DIRECTORY_FILE_FIGURES_HEADER = "# Figures:"
DIRECTORY_FILE_SEPARATOR = ": "

HEADING_PRODUCT_METADATA = "Product Metadata"
HEADING_TEST_METADATA = "Test Metadata"
HEADING_TEST_CASES = "Test Cases"
HEADING_GENERAL_INFO = "General Information"
HEADING_DETAILED_RESULTS = "Detailed Results"

HEADING_FIGURES = "Figures"
HEADING_FIGURE_N = "Figure %i"
HEADING_TEXTFILES = "Textfiles"
HEADING_TEXTFILE_N = "Textfile #%i"

MSG_NA = "N/A"

MSG_TARBALL_CORRUPT = "Tarball %s appears to be corrupt."

MSG_LINE_LIMIT = ("(only first %i lines of %s shown. The full textfile may be "
                  "retrieved from the tarball containing data for this test in this project's repository, "
                  "in the appropriate textfiles tarball for this test case.)")

HTML_TABLE_LINE_LIMIT = 1000
MSG_HTML_TABLE_LIMIT = MSG_LINE_LIMIT % (HTML_TABLE_LINE_LIMIT, "tables")
MD_TABLE_LINE_LIMIT = 100
MSG_MD_TABLE_LIMIT = MSG_LINE_LIMIT % (MD_TABLE_LINE_LIMIT, "tables")
TEXTFILE_LINE_LIMIT = 100
MSG_TEXTFILE_LIMIT = f"...\n{MSG_LINE_LIMIT % (TEXTFILE_LINE_LIMIT, 'textfiles')}"

logger = getLogger(__name__)


class OutputFormat(Enum):
    """Enum, specifying possible formats that the report is intended to ultimately be output in. When building for
    online compiled display, `HTML` will result in better formatting, while `MD` will result in better formatting when
    building for offline display.
    """
    MD = "markdown"
    HTML = "html"


class ValTestCaseMeta(NamedTuple):
    """Named tuple to contain output of a name of a test/testcase and its associated filename, plus optionally
    whether or not it passed.
    """
    name: str
    filename: str
    passed: Optional[bool] = None


class ValTestMeta(NamedTuple):
    """Named tuple to contain output of a test's name and filename, and a list of the same for all associated
    test cases.
    """
    name: str
    filename: str
    l_test_case_meta: Sequence[ValTestCaseMeta]
    num_passed: int = -1
    num_failed: int = -1


# Define the expected type for callables used to build test reports, now that the output type from it is defined above
BUILD_CALLABLE_TYPE = Callable[[Union[str, Dict[str, str]],
                                str,
                                Optional[str],
                                Optional[str],
                                OutputFormat], List[ValTestMeta]]


class FileInfo(NamedTuple):
    """NamedTuple containing file label, filename, and whether or not it's a figure.
    """
    label: Optional[str]
    filename: str
    is_figure: bool


class ReportSummaryWriter:
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

    For any of these cases, you will need to start by defining in a new module a child class of the ReportSummaryWriter
    class defined here, which overrides select methods, i.e.:

    ```
    class SpecificTestWriter(ReportSummaryWriter):

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

        # Add a heading for this section. The depth here is 2 (2 layers deeper than depth 0, which corresponds to the
        # highest level of heading within the body, which is labelled as "##"). We don't need any "#" or linebreak at
        # the end when adding the heading. We use the Requirement index in the label here to make sure it's unique.
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
                                                       reportdir,
                                                       datadir,
                                                       figures_tmpdir):
        writer.add_heading("Results and Figures", depth=0)

        # Dig out the data for each bin from the SupplementaryInfo
        req = test_case_results.l_requirements[0]
        supp_info_str = req.l_supp_info[0].info_value.strip()
        bin_1_str, bin_2_str = supp_info_str.split("\n\n")

        # Get the figure label and filename for each bin
        l_figure_labels_and_filenames = self._prepare_figures(test_case_results.analysis_result, reportdir, datadir,
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
            relative_figure_filename = self._move_figure_to_public(filename, reportdir, figures_tmpdir)

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

    # Class attribute definitions - these can be set either by overriding the values of the class attributes in child
    # classes or set at initialization

    # The name of the test, which will be used to name and title report pages
    test_name: Optional[str] = None

    # Whether any of the test cases are expected to have associated figures. If set to False, no Figures section will
    # be added to reports even if figures are present. If set to True and figures are not present, the section will
    # be present with "N/A"
    has_figures: bool = True

    # Same as `has_figures`, but for textfiles
    has_textfiles: bool = True

    # Instance attributes which are set when called
    output_format: Optional[OutputFormat] = None

    @log_entry_exit(logger)
    def __init__(self, **kwargs):
        """Initializer for ReportSummaryWriter, which allows specifying any desired attributes via kwargs. The
        allowed attributes are listed as class attributes above
        """

        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(
                    f"Class {self.__class__.__name__} has no attribute {key} which can be set at initialization.")
            setattr(self, key, value)

    @log_entry_exit(logger)
    def __call__(self, value, rootdir, reportdir=None, datadir=None, output_format=OutputFormat.HTML):
        """Template method which implements basic writing the summary of output for the test as a whole. Portions of
        this method which call protected methods can be overridden by child classes for customization.

        Parameters
        ----------
        value : str or Dict[str, str]
            The value provided in the .json manifest for this test. This should be either the filename of a tarball
            containing the test results product and associated datafiles, the filename of the data product,
            or a dict of keys pointing to multiple such files.
        rootdir : str
            The root directory of this project. All filenames provided should be relative to the "data" directory
            within `rootdir`.
        reportdir : str or None, default=None
            The directory to build reports in. Default: `rootdir`/public
        datadir : str or None, default=None
            If results data products are provided directly instead of as a tarball, this specifies the directory
            where the data files they point to can be found. Default: The directory containing the results data
            products.
        output_format : OutputFormat, default=OutputFormat.HTML
            The format that the report is intended to ultimately be output in. When building for online compiled
            display, `HTML` will result in better formatting, while `MD` will result in better formatting when
            building for offline display.

        Returns
        -------
        l_test_meta : List[ValTestMeta]
            A list of objects, each containing the test name and filename and a list of the same for associated
            tests. If the input `value` is a filename, this will be a single-element list. If the input `value` is
            instead a dict, this will have multiple elements, depending on the number of elements in the dict.
        """

        self.output_format = output_format

        if reportdir is None:
            reportdir = os.path.join(rootdir, PUBLIC_DIR)

        # Figure out how to interpret `value` by checking if it's a str or dict, and then iterate over call to
        # process each individual tarball
        l_test_meta: List[ValTestMeta]
        if isinstance(value, str):
            l_test_meta = self._summarize_results_file(value,
                                                       rootdir=rootdir,
                                                       reportdir=reportdir,
                                                       datadir=datadir,
                                                       tag=None)
        elif isinstance(value, dict):
            l_test_meta = []
            for sub_key, sub_value in value.items():
                l_test_meta += self._summarize_results_file(sub_value,
                                                            rootdir=rootdir,
                                                            reportdir=reportdir,
                                                            datadir=datadir,
                                                            tag=sub_key)
        else:
            raise ValueError("Value in manifest is of unrecognized type.\n"
                             f"Value was: {value}\n"
                             f"Type was: {type(value)}")

        return l_test_meta

    @log_entry_exit(logger)
    def _summarize_results_file(self, results_filename, rootdir, reportdir, datadir=None, tag=None):
        """Writes summary markdown files for the test results either contained in a tarball of the test results
        product and associated data or in a data product, with its data found relative to `datadir`.

        Parameters
        ----------
        results_filename : str
            The filename of a tarball containing the test results product and associated datafiles.
        rootdir : str
        reportdir : str
            The directory to build reports in.
        datadir : str or None
        tag : str or None
            If provided, this tag will be appended to the names of all test cases in the returned data, for purposes of
            separately labelling different instances of the same test.

        Returns
        -------
        l_test_meta : List[ValTestMeta]
            A list of objects containing the test name and filename and a list of the same for associated tests.
        """

        # Check for no input
        if results_filename is None:
            return []

        # Make sure the results_filename is fully-qualified
        results_filename = get_qualified_path(results_filename, base=os.path.join(rootdir, DATA_DIR))

        # Split execution depending on if we're passed a tarball or an XML data product

        if is_valid_tarball_filename(results_filename):
            qualified_tmpdir = self._make_tmpdir(results_filename, rootdir)

            # We use a try-finally block here to ensure the created datadir is removed after use
            try:
                qualified_results_tarball_filename = os.path.join(rootdir, DATA_DIR, results_filename)
                l_test_meta = self._summarize_results_tarball_with_tmpdir(qualified_results_tarball_filename,
                                                                          qualified_tmpdir,
                                                                          reportdir=reportdir,
                                                                          tag=tag)
            finally:
                shutil.rmtree(qualified_tmpdir)
        elif is_valid_xml_filename(results_filename):
            if datadir is None:
                datadir = os.path.split(results_filename)[0]
            l_test_meta = self._summarize_results_product(l_product_filenames=[results_filename],
                                                          reportdir=reportdir,
                                                          datadir=datadir,
                                                          tag=tag)
        else:
            raise ValueError(f"Filename {results_filename} is neither a valid and safe tarball filename nor a valid "
                             "XML filename.")

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
                                               reportdir,
                                               tag=None):
        """Writes summary markdown files for the test results contained in a tarball of the test results product and
        associated data, using a provided tmpdir for work.

        Parameters
        ----------
        qualified_results_tarball_filename : str
            The fully-qualified filename of a tarball containing the test results product and associated datafiles
        qualified_tmpdir : str
            The fully-qualified path to a temporary directory which can be used for this function.
        reportdir : str
        tag : str or None

        Returns
        -------
        l_test_meta : List[ValTestMeta]
        """

        extract_tarball(qualified_results_tarball_filename, qualified_tmpdir)

        l_product_filenames = self._find_product_filenames(qualified_tmpdir)
        l_qualified_product_filenames = [os.path.join(qualified_tmpdir, product_filename)
                                         for product_filename in l_product_filenames]

        # Make sure the required subdir exists before we start writing anything
        os.makedirs(os.path.join(reportdir, TEST_REPORTS_SUBDIR), exist_ok=True)

        l_test_meta = self._summarize_results_product(l_qualified_product_filenames, reportdir, qualified_tmpdir, tag)

        return l_test_meta

    @log_entry_exit(logger)
    def _summarize_results_product(self, l_product_filenames, reportdir, datadir, tag):
        """Writes summary markdown files for the test results contained in each of a list of data products. The
        output will be sorted based on PointingId, and so may not be in the same order as the input list
        `l_product_filenames`.

        Parameters
        ----------
        l_product_filenames : List[str]
            List of fully-qualified filenames of data products to generate reports for.
        reportdir : str
        datadir : str
            The directory where files referenced in the data products can be found.
        tag : str or None

        Returns
        -------
        l_test_meta : List[ValTestMeta]
        """

        # Get a list of test results, sorted by pointing ID
        l_test_results = [parse_xml_product(f) for f in l_product_filenames]
        l_test_results.sort(key=lambda a: a.pnt_id)

        l_test_meta: List[ValTestMeta] = []
        for test_results in l_test_results:

            test_name_tail = ""

            if tag is not None:
                test_name_tail += f"-{tag}"

            # If we're processing more than one product, ensure they're all named uniquely with their pointing ID
            if len(l_product_filenames) > 1:
                test_name_tail += f"-{test_results.pnt_id}"

            if self.test_name is None:
                test_name = f"TR-{test_results.product_id}{test_name_tail}"
            else:
                test_name = f"{self.test_name}{test_name_tail}"

            logger.info("Building report for test %s.", test_name)

            # We write the pages for the test cases first, so we know about and can link to them from the test
            # summary page
            l_test_case_meta = self._write_all_test_case_results(test_results=test_results,
                                                                 test_name_tail=test_name_tail,
                                                                 reportdir=reportdir,
                                                                 datadir=datadir)

            test_filename = self._write_test_results_summary(test_results=test_results,
                                                             test_name=test_name,
                                                             l_test_case_meta=l_test_case_meta,
                                                             reportdir=reportdir)

            num_passed, num_failed = self._calc_num_passed_failed(l_test_case_meta)
            l_test_meta.append(ValTestMeta(name=test_name,
                                           filename=test_filename,
                                           l_test_case_meta=l_test_case_meta,
                                           num_passed=num_passed,
                                           num_failed=num_failed))
        return l_test_meta

    @staticmethod
    @log_entry_exit(logger)
    def _calc_num_passed_failed(l_test_case_meta):
        """Calculates the number of test cases which have passed and failed from the provided list of ValTestCaseMeta.

        Parameters
        ----------
        l_test_case_meta : Sequence[ValTestCaseMeta]

        Returns
        -------
        num_passed : int
        num_failed : int
        """

        num_passed = sum([1 for x in l_test_case_meta if x.passed])
        num_failed = len(l_test_case_meta) - num_passed

        return num_passed, num_failed

    @log_entry_exit(logger)
    def _find_product_filenames(self, qualified_tmpdir):
        """Finds the filenames of all .xml products in the provided directory. If certain .xml files should be
        ignored for a given test, this method can be overridden to handle that.

        Parameters
        ----------
        qualified_tmpdir : str

        Returns
        -------
        l_product_filenames : List[str]
        """

        l_product_filenames = self._recursive_find_product_filenames(qualified_tmpdir)

        if len(l_product_filenames) == 0:
            raise ValueError("No .xml data products found in tarball.")

        return l_product_filenames

    @log_entry_exit(logger)
    def _recursive_find_product_filenames(self, qualified_dir: str) -> List[str]:
        """Recursive implementation of core loop in finding product filenames, to search within all subdirs.
        """

        l_product_filenames = [fn for fn in os.listdir(qualified_dir) if
                               os.path.isfile(os.path.join(qualified_dir, fn)) and self._is_valid_product_filename(fn)]

        l_subdirs = [subdir for subdir in os.listdir(qualified_dir) if
                     os.path.isdir(os.path.join(qualified_dir, subdir))]

        # Search recursively in each subdir
        for subdir in l_subdirs:
            qualified_subdir = os.path.join(qualified_dir, subdir)
            l_product_filenames += [os.path.join(subdir, fn) for fn in
                                    self._recursive_find_product_filenames(qualified_subdir)]

        return l_product_filenames

    @staticmethod
    @log_entry_exit(logger)
    def _is_valid_product_filename(filename):
        """Method to check if a filename is valid for a data product. By default, this just checks if it ends with
        ".xml", but this can be overridden for more detailed checks.

        Parameters
        ----------
        filename : str
            The filename to check for validity.

        Returns
        -------
        bool
        """
        return filename.endswith(".xml")

    @log_entry_exit(logger)
    def _write_all_test_case_results(self, test_results, test_name_tail, reportdir, datadir):
        """Writes out the results of all test cases to a .md-format file.

        Parameters
        ----------
        test_results : TestResults
            Object representing the read-in and parsed .xml product for test results.
        test_name_tail : str
            The extra "tail" added to the end of the test name, which will also be added to the end of all test case
            names.
        reportdir : str
        datadir : str

        Returns
        -------
        l_test_case_names_and_filenames : Sequence[ValTestCaseMeta]
            The names and generated file names of each test case associated with this test.
        """

        l_test_case_names = self._get_l_test_case_names(test_results, test_name_tail)

        l_test_case_names_and_filenames: List[ValTestCaseMeta] = []
        for test_case_results, test_case_name in zip(test_results.l_test_results, l_test_case_names):
            test_case_filename = os.path.join(TEST_REPORTS_SUBDIR, f"{test_case_name}.md")

            l_test_case_names_and_filenames.append(ValTestCaseMeta(name=test_case_name,
                                                                   filename=test_case_filename,
                                                                   passed=(test_case_results.global_result ==
                                                                           "PASSED")))

            # Now we defer to a sub-method to write the results, so the formatting in that bit can be easily overridden
            self._write_individual_test_case_results(test_case_results=test_case_results,
                                                     test_case_name=test_case_name,
                                                     test_case_filename=test_case_filename,
                                                     reportdir=reportdir,
                                                     datadir=datadir)

        return l_test_case_names_and_filenames

    @staticmethod
    @log_entry_exit(logger)
    def _get_l_test_case_names(test_results: TestResults, test_name_tail: str):
        """Generate names for each test case. This method can be overridden by child classes, but must result in
        unique names for each test case. In the default implementation, this uses the test case ID as the basis of
        the name, and in the case of clashes, appends an index to the name, e.g. "ID", "ID-2", "ID-3", etc.
        """

        d_test_name_instances: Dict[str, int] = {}
        l_test_case_names: List[str] = []

        for test_case_results in test_results.l_test_results:

            test_case_id = test_case_results.test_id
            if test_case_id in d_test_name_instances:
                d_test_name_instances[test_case_id] += 1
                test_case_name = f"{test_case_id}-{d_test_name_instances[test_case_id]}{test_name_tail}"
            else:
                d_test_name_instances[test_case_id] = 1
                test_case_name = f"{test_case_id}{test_name_tail}"

            l_test_case_names.append(test_case_name)

        return l_test_case_names

    @log_entry_exit(logger)
    def _write_individual_test_case_results(self,
                                            test_case_results,
                                            test_case_name,
                                            test_case_filename,
                                            reportdir,
                                            datadir):
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
        reportdir : str
        datadir : str
        """

        qualified_test_case_filename = os.path.join(reportdir, test_case_filename)

        logger.info("Writing results for test case %s from %s.", test_case_name, qualified_test_case_filename)

        # Ensure the folder for this exists
        os.makedirs(os.path.split(qualified_test_case_filename)[0], exist_ok=True)

        writer = TocMarkdownWriter(test_case_name)

        self._add_test_case_meta(writer, test_case_results)

        self._add_test_case_details_and_figures(test_case_results, writer, reportdir, datadir)

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

        writer.add_heading(HEADING_GENERAL_INFO, depth=0)
        writer.add_line(f"**Test Case ID:** {test_case_results.test_id}\n\n")
        writer.add_line(f"**Description:** {test_case_results.test_description}\n\n")
        writer.add_line(f"**Result:** {test_case_results.global_result}\n\n")
        if test_case_results.analysis_result.ana_comment is not None:
            writer.add_line(f"**Comments:** {test_case_results.analysis_result.ana_comment}\n\n")

    @log_entry_exit(logger)
    def _add_test_case_details_and_figures(self, test_case_results, writer, reportdir, datadir):
        """Adds lines for the supplementary info associated with an individual test case to a MarkdownWriter,
        prepares figures and textfiles, and also adds lines for them.

        Parameters
        ----------
        writer : TocMarkdownWriter
        test_case_results : SingleTestResult
        reportdir : str
        datadir : str
        """

        # Make a new datadir within the existing datadir for this batch of figures and textfiles (to avoid name clashes
        # with other test cases)
        figures_tmpdir = self._make_tmpdir(test_case_results, datadir)

        try:
            self._add_test_case_details_and_figures_with_tmpdir(writer, test_case_results, reportdir, datadir,
                                                                figures_tmpdir)
        finally:
            shutil.rmtree(figures_tmpdir)

    @log_entry_exit(logger)
    def _add_test_case_details_and_figures_with_tmpdir(self, writer, test_case_results, reportdir, datadir,
                                                       ana_files_tmpdir):
        """Adds lines for the supplementary info associated with an individual test case to a MarkdownWriter,
        prepares figures and textfiles, and also adds lines for them, after a temporary directory has been created to
        store figures data.

        In the default implementation, this method performs these tasks sequentially and separately since nothing
        can be assumed about how the supplementary info, figures, and textfiles relate. In child classes where the
        relationship is known, this may be overridden to handle them together if desired.

        Parameters
        ----------
        writer : TocMarkdownWriter
        test_case_results : SingleTestResult
        reportdir : str
        datadir : str
        ana_files_tmpdir : str
            The fully-qualified path to the temporary directory set up to contain extracted analysis files for this
            test case.
        """

        # Write the primary details for the test case
        self._add_test_case_details(writer, test_case_results)

        # Write details contained in analysis files (figures and textfiles)

        ana_result = test_case_results.analysis_result

        l_ana_files_labels_and_filenames = self._prepare_ana_files(ana_result=ana_result,
                                                                   reportdir=reportdir,
                                                                   datadir=datadir,
                                                                   ana_files_tmpdir=ana_files_tmpdir)

        self._add_test_case_figures(writer=writer,
                                    reportdir=reportdir,
                                    ana_files_tmpdir=ana_files_tmpdir,
                                    l_ana_files_labels_and_filenames=l_ana_files_labels_and_filenames)
        self._add_test_case_textfiles(writer=writer,
                                      ana_files_tmpdir=ana_files_tmpdir,
                                      l_ana_files_labels_and_filenames=l_ana_files_labels_and_filenames)

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
        writer.add_heading(HEADING_DETAILED_RESULTS, depth=0)
        for req_i, req in enumerate(test_case_results.l_requirements):
            writer.add_heading("Requirement", depth=1)
            self._add_measured_parameter_line(writer, req)
            self._add_measured_value_line(writer, req)
            if req.req_comment is not None:
                writer.add_line(f"**Comments**: {req.req_comment}\n\n")
            self._add_test_case_supp_info(writer, req)

    @staticmethod
    @log_entry_exit(logger)
    def _add_measured_parameter_line(writer, req):
        """Adds a line for the measured parameter associated with an individual test case to a MarkdownWriter.

        Parameters
        ----------
        writer : TocMarkdownWriter
        req : RequirementResults
            The object containing the results for a specific requirement.
        """
        writer.add_line(f"**Measured Parameter**: {req.meas_value.parameter}\n\n")

    @staticmethod
    @log_entry_exit(logger)
    def _add_measured_value_line(writer, req):
        """Adds a line for the measured value associated with an individual test case to a MarkdownWriter.

        Parameters
        ----------
        writer : TocMarkdownWriter
        req : RequirementResults
            The object containing the results for a specific requirement.
        """
        writer.add_line(f"**Measured Value**: {req.meas_value.value}\n\n")

    @staticmethod
    @log_entry_exit(logger)
    def _add_test_case_supp_info(writer, req):
        """Adds lines for the supplementary info associated with an individual test case to a MarkdownWriter.

        Parameters
        ----------
        writer : TocMarkdownWriter
        req : RequirementResults
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
    def _prepare_ana_files(self, ana_result, reportdir, datadir, ana_files_tmpdir):
        """Performs standard steps to prepare figures and textfiles - unpacking them, reading the directory file,
        and setting up expected output directory.

        Parameters
        ----------
        ana_result : AnalysisResult
            Object containing information about the textfiles and figures for a given test case.
        reportdir : str
        datadir : str
        ana_files_tmpdir : str
            The tmpdir to be used to extract the textfiles and figures in their respective tarballs.

        Returns
        -------
        l_ana_files_labels_and_filenames : List[Tuple[str or None,str]] or None
            A list of (label,filename) tuples which were read in from the directory file. If expected files are not
            present, None will be returned instead.
        """

        # Check if any figures are present
        if ana_result.figures_tarball is None or ana_result.textfiles_tarball is None:
            # None present, but this might be expected, so just log at debug level
            logger.debug("No figures associated with this test case.")
            return None

        # Extract the textfiles and figures tarballs
        qualified_textfiles_tarball_filename = get_data_filename(ana_result.textfiles_tarball, datadir)
        qualified_figures_tarball_filename = get_data_filename(ana_result.figures_tarball, datadir)

        # Return None if either expected tarball doesn't exist
        if qualified_textfiles_tarball_filename is None or qualified_figures_tarball_filename is None:
            return None

        try:
            extract_tarball(qualified_figures_tarball_filename, ana_files_tmpdir)
        except ValueError:
            logger.error(MSG_TARBALL_CORRUPT, qualified_figures_tarball_filename)
            return None
        try:
            extract_tarball(qualified_textfiles_tarball_filename, ana_files_tmpdir)
        except ValueError:
            logger.error(MSG_TARBALL_CORRUPT, qualified_textfiles_tarball_filename)
            return None

        # Find the "directory" file which should have been in the tarball, and get the labels and filenames of
        # figures from it
        try:
            qualified_directory_filename = self.find_directory_filename(ana_files_tmpdir)
        except (FileNotFoundError, ValueError) as e:
            logger.error(str(e) + " This occurred when unpacking tarball %s", qualified_textfiles_tarball_filename)
            return None

        l_ana_files_labels_and_filenames = self.read_ana_files_labels_and_filenames(qualified_directory_filename)

        # Make sure a data subdir exists in the images dir
        os.makedirs(os.path.join(reportdir, IMAGES_SUBDIR, DATA_DIR), exist_ok=True)

        return l_ana_files_labels_and_filenames

    @log_entry_exit(logger)
    def _add_test_case_figures(self, writer, reportdir, ana_files_tmpdir, l_ana_files_labels_and_filenames):
        """Prepares figures and adds lines for them to a MarkdownWriter, after a new temporary directory has been
        created to store extracted files in.

        Parameters
        ----------
        writer : TocMarkdownWriter
        reportdir : str
        ana_files_tmpdir : str
            The fully-qualified path to the temporary directory set up to contain figures data for this test case.
        l_ana_files_labels_and_filenames : List[FileInfo] or None
            A list of (label,filename) tuples which were read in from the directory file. If expected files were not
            present, this will be None instead
        """

        # Don't output anything if this class is defined as not having figures
        if not self.has_figures:
            return

        writer.add_heading(HEADING_FIGURES, depth=0)

        # Check we prepared successfully; if not, return, so we don't hit any further errors
        if not l_ana_files_labels_and_filenames:
            writer.add_line(f"{MSG_NA}\n\n")
            return

        some_figures_added = False

        # Add a subsection for each figure to the writer
        for i, file_info in enumerate(l_ana_files_labels_and_filenames):

            if not file_info.is_figure:
                continue
            else:
                some_figures_added = True

            # Make a label if we don't have one
            label = file_info.label
            if label is None:
                label = HEADING_FIGURE_N % i

            relative_figure_filename = self._move_figure_to_public(file_info.filename, reportdir, ana_files_tmpdir)

            writer.add_heading(label, depth=1)
            writer.add_line(f"![{label}]({relative_figure_filename})\n\n")

        # Check if we output any figures, and output N/A if not
        if not some_figures_added:
            writer.add_line(f"{MSG_NA}\n\n")
            return

    @staticmethod
    @log_entry_exit(logger)
    def _move_figure_to_public(filename, reportdir, ana_files_tmpdir):
        """Move a figure to the appropriate directory and return the relative filename for it.

        Parameters
        ----------
        filename : str
            The filename of the figure relative to the `figures_tmpdir`
        reportdir : str
        ana_files_tmpdir : str
            The fully-qualified path to the tmpdir created to store unpacked figures.

        Returns
        -------
        relative_figure_filename : str or None
            The path to the moved figure relative to where test reports are stored. In case of an error where the
            file wasn't present, the error will be logged and None will be returned instead.
        """

        qualified_src_filename = os.path.join(ana_files_tmpdir, filename)
        qualified_dest_filename = os.path.join(reportdir, IMAGES_SUBDIR, filename)

        # Check for file existence
        if not os.path.isfile(qualified_src_filename):
            # Source doesn't exist. If destination does, then there's no issue - presumably it's already been moved
            # for another page, and so we don't need to move it again. If destination doesn't exist, then we have an
            # error.
            if not os.path.isfile(qualified_dest_filename):
                logger.error(f"Expected figure {filename} does not exist.")
                return None
        else:
            shutil.move(qualified_src_filename, qualified_dest_filename)

        # Return the path to the moved figure file, relative to where test reports will be stored
        return f"../{IMAGES_SUBDIR}/{filename}"

    @log_entry_exit(logger)
    def _add_test_case_textfiles(self, writer, ana_files_tmpdir, l_ana_files_labels_and_filenames):
        """Prepares textfiles and adds lines for them to a MarkdownWriter, after a new temporary directory has been
        created to store extracted files in.

        Parameters
        ----------
        writer : TocMarkdownWriter
        ana_files_tmpdir : str
            The fully-qualified path to the temporary directory set up to contain figures data for this test case.
        l_ana_files_labels_and_filenames : List[FileInfo] or None
        """

        # Don't output anything if this class is defined as not having textfiles
        if not self.has_textfiles:
            return

        writer.add_heading(HEADING_TEXTFILES, depth=0)

        # Check we prepared successfully; if not, return, so we don't hit any further errors
        if not l_ana_files_labels_and_filenames:
            writer.add_line(f"{MSG_NA}\n\n")
            return

        some_textfiles_added = False

        # Add a subsection for each textfile to the writer
        for i, file_info in enumerate(l_ana_files_labels_and_filenames):

            if file_info.is_figure:
                continue
            else:
                some_textfiles_added = True

            # Make a label if we don't have one
            label = file_info.label
            if label is None:
                label = HEADING_TEXTFILE_N % i

            writer.add_heading(label, depth=1)

            qualified_filename = os.path.join(ana_files_tmpdir, file_info.filename)

            # Check if the file contains a table, and print it neatly if so
            try:
                table = Table.read(qualified_filename)
                self._add_table_contents(writer=writer, table=table)
            except IORegistryError:
                # Fall back to printing raw contents of the file
                self._add_raw_textfile_contents(writer=writer, qualified_filename=qualified_filename)

        # Check if we output any textfiles, and output N/A if not
        if not some_textfiles_added:
            writer.add_line(f"{MSG_NA}\n\n")
            return

    @log_entry_exit(logger)
    def _add_table_contents(self, writer, table):
        """Adds the contents of an astropy table to a markdown writer. The formatting depends on the current
        execution mode - will be markdown-formatted if called via standalone `build_report.py` script,
        or html-formatted if called via the `build_all_report_pages.py` script.

        Parameters
        ----------
        writer : TocMarkdownWriter
        table : Table
            An astropy table, which is to be printed out cleanly in the markdown writer
        """

        if self.output_format == OutputFormat.HTML:
            self._add_table_contents_html(writer, table)
        elif self.output_format == OutputFormat.MD:
            self._add_table_contents_md(writer, table)
        else:
            raise ValueError(f"Unrecognized output format: {self.output_format=}")

    @staticmethod
    @log_entry_exit(logger)
    def _add_table_contents_html(writer, table):
        """Adds the contents of an astropy table to a markdown writer, formatted as an html table

        Parameters
        ----------
        writer : TocMarkdownWriter
        table : Table
        """

        # Put the table in a scrollable div container
        writer.add_line("<div class=\"tableContainer\">\n<table>\n")

        # Add the table header

        writer.add_line("<tr>\n")
        for colname in table.colnames:
            writer.add_line(f"<th><strong>{colname}</strong></th>\n")
        writer.add_line("</tr>\n")

        # Start the table body
        writer.add_line("<tbody>\n")

        # Add data for each row
        hit_row_limit = False
        for row_index, row in enumerate(table):

            if row_index >= HTML_TABLE_LINE_LIMIT:
                hit_row_limit = True
                break

            writer.add_line("<tr>\n")

            # Add each item in the row
            for item in row:
                # Convert each item into a string, and remove any linebreaks in that string
                cleaned_item = str(item).replace("\n", "")
                writer.add_line(f"<td>{cleaned_item}</td>\n")

            writer.add_line("</tr>\n")

        # Close the table body, table, and div
        writer.add_line("</tbody>\n</table>\n</div>\n\n")

        # If we hit the row limit, make a note of this
        if hit_row_limit:
            writer.add_line(f"{MSG_HTML_TABLE_LIMIT}\n\n")

    @staticmethod
    @log_entry_exit(logger)
    def _add_table_contents_md(writer, table):
        """Adds the contents of an astropy table to a markdown writer, formatted as a markdown table

        Parameters
        ----------
        writer : TocMarkdownWriter
        table : Table
        """

        # Add a header row with the column names, then a separator line below it

        num_columns = len(table.colnames)

        writer.add_line((("| **%s** " * num_columns) + "|\n") % tuple(table.colnames))
        writer.add_line("|:--" * num_columns + "|\n")

        # Add data for each row

        row_line_template = ("| %s " * num_columns) + "|"
        hit_row_limit = False

        for row_index, row in enumerate(table):

            if row_index >= MD_TABLE_LINE_LIMIT:
                hit_row_limit = True
                break
            row_line = row_line_template % tuple(map(str, row))

            # Clean the line of any newlines and add it to the writer
            row_line_cleaned = row_line.replace("\n", "")
            writer.add_line(f"{row_line_cleaned}\n")

        # Add an extra linebreak after the table
        writer.add_line("\n")

        # If we hit the row limit, make a note of this
        if hit_row_limit:
            writer.add_line(f"{MSG_MD_TABLE_LIMIT}\n\n")

    @staticmethod
    @log_entry_exit(logger)
    def _add_raw_textfile_contents(writer, qualified_filename):
        """Adds the contents of a textfile directly to a maths section, without any modification.

        Parameters
        ----------
        writer : TocMarkdownWriter
        qualified_filename : str
            The fully-qualified filename of the textfile
        """
        # Read in the textfile in and write out its contents in a math section to avoid formatting issues
        writer.add_line("```\n")
        for line_index, line in enumerate(open(qualified_filename, "r")):
            if line_index >= TEXTFILE_LINE_LIMIT:
                writer.add_line(f"{MSG_TEXTFILE_LIMIT}\n")
                break
            # Lines read in this way already include a linebreak at the end, so we don't need to add one in
            writer.add_line(line)
        writer.add_line("```\n\n")

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
    def read_ana_files_labels_and_filenames(qualified_directory_filename):
        """Reads a directory file, and returns a list of analysis file labels and filenames. Note that any file label
        might be None if it's not supplied in the directory file.

        Parameters
        ----------
        qualified_directory_filename : str
            The fully-qualified path to the directory file.

        Returns
        -------
        l_ana_files_labels_and_filenames: List[FileInfo] or None
        """

        # Use the directory to find labels for figures, if it has them. Otherwise, just use it as a list of the figures
        with open(qualified_directory_filename, "r") as fi:
            l_directory_lines = fi.readlines()

        l_ana_files_labels_and_filenames: List[Tuple[Optional[str], str, bool]] = []
        textfiles_section_started = False
        figures_section_started = False
        for directory_line in l_directory_lines:
            directory_line = directory_line.strip()

            # If we haven't started the textfiles section, check for the header which starts it and then start reading
            # on the next iteration
            if not textfiles_section_started:
                if directory_line == DIRECTORY_FILE_TEXTFILES_HEADER:
                    textfiles_section_started = True
                    figures_section_started = False
                continue
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
                l_ana_files_labels_and_filenames.append(FileInfo(label=figure_label,
                                                                 filename=figure_filename,
                                                                 is_figure=figures_section_started))

        return l_ana_files_labels_and_filenames

    @log_entry_exit(logger)
    def _write_test_results_summary(self, test_results, test_name, l_test_case_meta, reportdir):
        """Writes out the summary of the test to a .md-format file. If special formatting is desired for an
        individual test, this method or the methods it calls can be overridden by child classes.

        Parameters
        ----------
        test_results : TestResults
        test_name : str
            The name of this test.
        l_test_case_meta : Sequence[ValTestCaseMeta]
            The names and file names of each test case associated with this test.
        reportdir : str

        Returns
        -------
        test_filename : str
            The filename of the created .md file containing the summary of this test, relative to "public" directory
            within `rootdir`
        """

        test_filename = os.path.join(TEST_REPORTS_SUBDIR, f"{test_name}.md")

        qualified_test_filename = os.path.join(reportdir, test_filename)

        logger.info("Writing test results summary to %s", qualified_test_filename)

        writer = TocMarkdownWriter(test_name)

        self._add_product_metadata(writer, test_results)
        self._add_test_metadata(writer, test_results)
        self._add_test_case_table(writer, test_results, l_test_case_meta)

        # Ensure the folder for this exists
        os.makedirs(os.path.split(qualified_test_filename)[0], exist_ok=True)

        with open(qualified_test_filename, "w") as fo:
            writer.write(fo)

        return test_filename

    @staticmethod
    @log_entry_exit(logger)
    def _add_product_metadata(writer, test_results):
        """Writes metadata related to the test's data product to an open filehandle

        Parameters
        ----------
        writer : TocMarkdownWriter
            A writer to handle storing heading and lines we wish to be written out to a file
        test_results : TestResults
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
    def _add_test_metadata(writer, test_results):
        """Writes metadata related to the test itself to an open filehandle

        Parameters
        ----------
        writer : TocMarkdownWriter
        test_results : TestResults
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
    def _add_test_case_table(self, writer, test_results, l_test_case_meta):
        """Writes a table containing test case information and links to their pages to an open filehandle.

        Parameters
        ----------
        writer : TocMarkdownWriter
        test_results : TestResults
        l_test_case_meta : Sequence[ValTestCaseMeta]
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
