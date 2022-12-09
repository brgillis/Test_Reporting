"""
:file: Test_Reporting/utility/product_parsing.py

:date: 10/14/2022
:author: Bryan Gillis

This python module provides functionality to help with parsing of SheValidationTestResults products. The goal of the
functions here is to provide the relevant information in an output dataclass of defined format which can be easily
inspected with an IDE or in a python instance to see its structure, rather than the raw XML element structure which
requires the user to know its structure.

This module defines a hierarchy of dataclasses (`TestResults` being at the top of the hierarchy), for which the data
which was stored in the XML file can be accessed as simple attributes, e.g. `test_results.l_test_results[
0].global_result`. Each of these dataclasses has a classmethod called `make_from_element` which is used to construct
it from the XML element which contains the corresponding data.

The `parse_xml_product` method is used to construct the full `TestResults` object hierarchically - its
`make_from_element` method is called on the root element of the XML file, it reads in simple elements from the XML
file directly (converting to the expected types) and constructs other dataclasses via their own `make_from_element`
methods, which proceed similarly.

If the structure of the SheValidationTestResults data products changes, this module will need to be updated to reflect
those changes. Similarly, not all the XML file's metadata is currently being read in here; if some missing data
is later needed, this will also have to be updated.
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

from dataclasses import dataclass, field
from datetime import datetime
from logging import getLogger
from typing import Any, List, Optional, Type
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from Test_Reporting.utility.misc import ensure_data_prefix, log_entry_exit

logger = getLogger(__name__)


@dataclass
class MeasuredValue:
    """Dataclass containing information from a SheValidationTestResults data product, corresponding to one of the
    `root.Data.ValidationTestList.ValidatedRequirements.Requirement.MeasuredValue` elements.
    """

    parameter: str
    data_type: str
    value: Any

    @classmethod
    @log_entry_exit(logger)
    def make_from_element(cls, e):
        """Construct an instance of this class from a corresponding XML element. In the case of this class,
        it should be constructed from one of the
        `root.Data.ValidationTestList.ValidatedRequirements.Requirement.MeasuredValue` elements of the ElementTree.

        Parameters
        ----------
        e : Element
            A `root.Data.ValidationTestList.ValidatedRequirements.Requirement.MeasuredValue` element of the
            ElementTree of an opened SheValidationTestResults XML data product.

        Returns
        -------
        MeasuredValue
        """

        data_type = _element_find(e, "DataType", output_type=str)
        if data_type == "float":
            value = _element_find(e, "Value.FloatValue", output_type=float)
        elif data_type == "int":
            value = _element_find(e, "Value.IntValue", output_type=int)
        else:
            value = _element_find(e, "Value.StringValue", output_type=str)

        return MeasuredValue(parameter=_element_find(e, "Parameter", output_type=str),
                             data_type=data_type,
                             value=value)


@dataclass
class SupplementaryInfo:
    """Dataclass containing information from a SheValidationTestResults data product, corresponding to one of the
    `root.Data.ValidationTestList.ValidatedRequirements.Requirement.SupplementaryInformation.Parameter` elements.
    """

    info_key: str
    info_description: str
    info_value: str

    @classmethod
    @log_entry_exit(logger)
    def make_from_element(cls, e):
        """Construct an instance of this class from a corresponding XML element. In the case of this class,
        it should be constructed from one of the
        `root.Data.ValidationTestList.ValidatedRequirements.Requirement.SupplementaryInformation.Parameter` elements
        of the ElementTree.

        Parameters
        ----------
        e : Element
            A `root.Data.ValidationTestList.ValidatedRequirements.Requirement.SupplementaryInformation.Parameter`
            element of the ElementTree of an opened SheValidationTestResults XML data product.

        Returns
        -------
        SupplementaryInfo
        """
        return SupplementaryInfo(info_key=_element_find(e, "Key", output_type=str),
                                 info_description=_element_find(e, "Description", output_type=str),
                                 info_value=_element_find(e, "StringValue", output_type=str))


@dataclass
class RequirementResults:
    """Dataclass containing information from a SheValidationTestResults data product, corresponding to one of the
    `root.Data.ValidationTestList.ValidatedRequirements` elements.
    """

    req_id: str
    meas_value: MeasuredValue
    req_result: str
    req_comment: Optional[str] = None
    l_supp_info: List[SupplementaryInfo] = field(default_factory=list)

    @classmethod
    @log_entry_exit(logger)
    def make_from_element(cls, e):
        """Construct an instance of this class from a corresponding XML element. In the case of this class,
        it should be constructed from one of the `root.Data.ValidationTestList.ValidatedRequirements` elements of the
        ElementTree.

        Parameters
        ----------
        e : Element
            A `root.Data.ValidationTestList.ValidatedRequirements` element of the ElementTree of an opened
            SheValidationTestResults XML data product.

        Returns
        -------
        RequirementResults
        """

        meas_value = MeasuredValue.make_from_element(_element_find(e, "Requirement.MeasuredValue"))
        l_supp_info = [SupplementaryInfo.make_from_element(sub_e) for sub_e in
                       _element_find(e, "Requirement.SupplementaryInformation.Parameter", find_all=True)]

        return RequirementResults(req_id=_element_find(e, "Requirement.Id", output_type=str),
                                  meas_value=meas_value,
                                  req_result=_element_find(e, "Requirement.ValidationResult", output_type=str),
                                  req_comment=_element_find(e, "Requirement.Comment", output_type=str),
                                  l_supp_info=l_supp_info)


@dataclass
class AnalysisResult:
    """Dataclass containing information from a SheValidationTestResults data product, corresponding to one of the
    `root.Data.ValidationTestList.AnalysisResult` elements.
    """

    ana_result: str
    textfiles_tarball: Optional[str] = None
    figures_tarball: Optional[str] = None
    ana_comment: Optional[str] = None

    def __post_init__(self):
        """Fix potential issues with filenames, to ensure they always start with "data/"."""

        self.textfiles_tarball = ensure_data_prefix(self.textfiles_tarball)
        self.figures_tarball = ensure_data_prefix(self.figures_tarball)

    @classmethod
    @log_entry_exit(logger)
    def make_from_element(cls, e):
        """Construct an instance of this class from a corresponding XML element. In the case of this class,
        it should be constructed from one of the `root.Data.ValidationTestList.AnalysisResult` elements of the
        ElementTree.

        Parameters
        ----------
        e : Element
            A `root.Data.ValidationTestList.AnalysisResult` element of the ElementTree of an opened
            SheValidationTestResults XML data product.

        Returns
        -------
        AnalysisResult
        """
        return AnalysisResult(ana_result=_element_find(e, "Result", output_type=str),
                              textfiles_tarball=_element_find(e, "AnalysisFiles.TextFiles.FileName", output_type=str),
                              figures_tarball=_element_find(e, "AnalysisFiles.Figures.FileName", output_type=str),
                              ana_comment=_element_find(e, "Comment", output_type=str))


@dataclass
class SingleTestResult:
    """Dataclass containing information from a SheValidationTestResults data product, corresponding to one of the
    `root.Data.ValidationTestList` elements.
    """

    # Attributes specially added to the SHE implementation
    test_id: str
    test_description: str
    global_result: str

    l_requirements: List[RequirementResults] = field(default_factory=list)
    analysis_result: Optional[AnalysisResult] = None

    @classmethod
    @log_entry_exit(logger)
    def make_from_element(cls, e):
        """Construct an instance of this class from a corresponding XML element. In the case of this class,
        it should be constructed from one of the `root.Data.ValidationTestList` elements of the ElementTree.

        Parameters
        ----------
        e : Element
            A `root.Data.ValidationTestList` element of the ElementTree of an opened SheValidationTestResults XML data
            product.

        Returns
        -------
        SingleTestResult
        """

        l_requirements = [RequirementResults.make_from_element(sub_e) for sub_e in
                          _element_find(e, "ValidatedRequirements", find_all=True)]
        analysis_result = AnalysisResult.make_from_element(_element_find(e, "AnalysisResult"))

        return SingleTestResult(test_id=_element_find(e, "TestId", output_type=str),
                                test_description=_element_find(e, "TestDescription", output_type=str),
                                global_result=_element_find(e, "GlobalResult", output_type=str),
                                l_requirements=l_requirements,
                                analysis_result=analysis_result)


@dataclass
class TestResults:
    """Dataclass containing information from a SheValidationTestResults data product, corresponding to the full product.
    """

    # Metadata stored in the header
    product_id: str
    dataset_release: str
    plan_id: str
    ppo_id: str
    pipeline_definition_id: str
    creation_date: datetime

    # Metadata stored in the data section
    exp_product_id: Optional[str] = None
    obs_id: Optional[int] = None
    pnt_id: Optional[int] = None
    obs_mode: Optional[str] = "Wide"
    n_exp: Optional[int] = None
    tile_id: Optional[int] = None
    source_pipeline: str = "sheAnalysis"

    # Data
    l_test_results: List[SingleTestResult] = field(default_factory=list)

    @classmethod
    @log_entry_exit(logger)
    def make_from_element(cls, e):
        """Construct an instance of this class from a corresponding XML element. In the case of this class,
        it should be constructed from the root element of the ElementTree.

        Parameters
        ----------
        e : Element
            The root element of the ElementTree of an opened SheValidationTestResults XML data product.

        Returns
        -------
        TestResults
        """

        l_test_results = [SingleTestResult.make_from_element(sub_e) for sub_e in
                          _element_find(e, "Data.ValidationTestList", find_all=True)]
        creation_date = _construct_datetime(_element_find(e, "Header.CreationDate", output_type=str))

        return TestResults(product_id=_element_find(e, "Header.ProductId", output_type=str),
                           dataset_release=_element_find(e, "Header.DataSetRelease", output_type=str),
                           plan_id=_element_find(e, "Header.PlanId", output_type=str),
                           ppo_id=_element_find(e, "Header.PPOId", output_type=str),
                           pipeline_definition_id=_element_find(e, "Header.PipelineDefinitionId", output_type=str),
                           creation_date=creation_date,
                           exp_product_id=_element_find(e, "Data.ExposureProductId", output_type=str),
                           obs_id=_element_find(e, "Data.ObservationId", output_type=int),
                           pnt_id=_element_find(e, "Data.PointingId", output_type=int),
                           obs_mode=_element_find(e, "Data.ObservationMode", output_type=str),
                           n_exp=_element_find(e, "Data.NumberExposures", output_type=int),
                           tile_id=_element_find(e, "Data.TileId", output_type=int),
                           source_pipeline=_element_find(e, "Data.SourcePipeline", output_type=str),
                           l_test_results=l_test_results)


@log_entry_exit(logger)
def _element_find(element, tag, find_all=False, output_type=None):
    """Gets a sub-element or list thereof from an XML ElementTree Element, searching recursively as necessary,
    optionally converting it into an object of the provided type.

    Parameters
    ----------
    element : Element
        The element in an XML ElementTree from which to generate the output object.
    tag : str
        The tag to search for, which may be a period (.) separated set of tags to work through recursively,
        e.g. "tag.subtag".
    find_all : bool, default=False
        If False, will return the results of `element.find` in final step, which returns a single value. If True,
        will return the results of `element.findall` in the final step, which returns a list of all values.
    output_type : type or None, default=None
        If None, will return the Element directly. If str, int, or float, will convert to this type if the Element is
        not None, and will return None if it is None.

    Returns
    -------
    Element or output_type or List[Element] or List[output_type]
        The sub-element for the given tag, or else the representation of it in the desired output_type if requested.
        If `find_all==True`, a list of matching elements or their representations in the desired type will be returned
        instead.
    """

    # Check for simple case, to break out of recursion
    if "." not in tag:
        if find_all:
            l_output = element.findall(tag)
            if output_type is not None:
                l_output = [_e_to_type(output, output_type) for output in l_output]
            return l_output
        else:
            output = element.find(tag)
            if output_type is not None:
                output = _e_to_type(output, output_type)
            return output

    # Otherwise, split on the first "." and call this method recursively
    head, tail = tag.split(".", maxsplit=1)
    return _element_find(element.find(head), tail, find_all=find_all, output_type=output_type)


def _construct_datetime(s: str) -> datetime:
    """Converts a string value, formatted like "YYYY-MM-DDTHH:MM:SS.408Z", into a datetime object.
    """

    # Pad milliseconds with zeros if it's been truncated
    s_before_z = s.split('Z')[0]
    s_before_milli, s_milli = s_before_z.split(',')
    while len(s_milli) < 3:
        s_milli += "0"

    # Reconstruct in ISO format
    s_iso = f"{s_before_milli}.{s_milli}+00:00"

    return datetime.fromisoformat(s_iso)


def _e_to_type(e: Optional[Element], t: Type) -> Optional[str]:
    """Tries to convert an XML element to the provided type. Returns None if None is provided
    """
    if e is None:
        return None
    return t(e.text)


@log_entry_exit(logger)
def parse_xml_product(filename):
    """Parses a SheValidationTestResults XML product, returning a TestResults dataclass containing the information
    within it.

    Parameters
    ----------
    filename : str
        The fully-qualified filename of the SheValidationTestResults XML product to parse

    Returns
    -------
    parsed_xml_product : TestResults
    """

    tree = ElementTree.parse(filename)

    return TestResults.make_from_element(tree.getroot())
