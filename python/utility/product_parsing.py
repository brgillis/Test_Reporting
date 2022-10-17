"""
:file: utility/product_parsing.py

:date: 10/14/2022
:author: Bryan Gillis

This python module provides functionality to help with parsing of SheValidationTestResult products. The goal of the
functions here is to provide the relevant information in an output dataclass of defined format, which can then be
written to output Markdown files.
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

from dataclasses import Field, dataclass, field
from datetime import datetime
from logging import getLogger
from typing import Any, Dict, List, Literal, Optional, TypeVar
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

logger = getLogger(__name__)

@dataclass
class Tags:
    """A special dataclass which defines the XML tags which we wish to read data from. The name of each attribute in
    this class corresponds to the name of the attribute in the associated dataclass which will store the information
    contained within that entry.
    """

    # Data stored in the SupplementaryInfo dataclass
    info_key: str = "Key"
    info_description: str = "Description"
    info_value: str = "StringValue"

    # Data stored in the RequirementResults dataclass
    req_id = "Requirement.Id"
    meas_value = "Requirement.MeasuredValue"
    req_result = "Requirement.ValidationResult"
    req_comment = "Requirement.Comment"
    l_supp_info = "Requirement.SupplementaryInformation.Parameter"

    # Data stored in the AnalysisResult dataclass
    ana_result = "Result"
    textfiles_tarball = "AnalysisFiles.TextFiles.FileName"
    figures_tarball = "AnalysisFiles.Figures.FileName"
    ana_comment = "Comment"

    # Data stored in the SingleTestResult dataclass
    test_id = "TestId"
    test_description = "TestDescription"
    global_result = "GlobalResult"
    l_requirements = "ValidatedRequirements"
    analysis_result = "AnalysisResult"

    # Data stored in the TestResults dataclass
    product_id = "Header.ProductId"
    dataset_release = "Header.DataSetRelease"
    plan_id = "Header.PlanId"
    ppo_id = "Header.PPOId"
    pipeline_definition_id = "Header.PipelineDefinitionId"
    creation_date = "Header.CreationDate"
    exp_product_id = "Data.ExposureProductId"
    obs_id = "Data.ObservationId"
    pnt_id = "Data.PointingId"
    obs_mode = "Data.ObservationMode"
    n_exp = "Data.NumberExposures"
    tile_id = "Data.TileId"
    source_pipeline = "Data.SourcePipeline"
    l_test_results = "Data.ValidationTestList"


@dataclass
class SupplementaryInfo:
    info_key: str
    info_description: str
    info_value: str


@dataclass
class RequirementResults:
    req_id: str
    meas_value: Any
    req_result: Literal["PASSED", "FAILED"]
    req_comment: Optional[str] = None
    l_supp_info: List[SupplementaryInfo] = field(default_factory=list)


@dataclass
class AnalysisResult:
    ana_result: str
    textfiles_tarball: Optional[str] = None
    figures_tarball: Optional[str] = None
    ana_comment: Optional[str] = None


@dataclass
class SingleTestResult:

    # Attributes specially added to the SHE implementation
    test_id: str
    test_description: str
    global_result: str

    l_requirements: List[RequirementResults] = field(default_factory=list)
    analysis_result: Optional[AnalysisResult] = None


@dataclass
class TestResults:

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


S_XML_OBJECT_TYPES = {TestResults, SingleTestResult, RequirementResults, AnalysisResult, SupplementaryInfo}

OutputType = TypeVar("OutputType")


def recursive_element_find(element, tag, find_all=False):
    """Gets a sub-element from an XML ElementTree Element, searching recursively as necessary.

    Parameters
    ----------
    element : Element
        The element in an XML ElementTree from which to generate the output object
    tag : str
        The tag to search for, which may be a period (.) separated set of tags to work through recursively
    find_all : bool, default=False
        If False, will return the results of `element.find` in final step, which returns a single value. If True,
        will return the results of `element.findall` in the final step, which returns a list of all values.

    Returns
    -------
    sub_element : Element
        The sub-element for the given tag
    """

    # Check for simple case, to break out of recursion
    if "." not in tag:
        if find_all:
            return element.findall(tag)
        else:
            return element.find(tag)

    # Otherwise, split on the first . and call this method recursively
    head, tail = tag.split(".", maxsplit=1)
    return recursive_element_find(element.find(head), tail, find_all=find_all)


def construct_datetime(s):
    """Converts a string value, formatted like "YYYY-MM-DDTHH:MM:SS.408Z", into a datetime object.

    Parameters
    ----------
    s : str
        The string value to be converted

    Returns
    -------
    dt : datetime
        The datetime object equivalent of the input string
    """

    dt = datetime.fromisoformat(s.replace('Z', '+00:00'))

    return dt


def get_constructor(output_type):
    """Get a constructor that can be called on a str to convert it to the desired output type. This works by checking
    first for known types which need special handling, and then defaulting to using the type itself as a constructor.

    Parameters
    ----------
    output_type : Type[OutputType]
        The type of the object to be generated.

    Returns
    -------
    constructor : Callable[[str], OutputType]
        An appropriate constructor for this type

    """

    if output_type == datetime:
        return construct_datetime

    return output_type


def create_from_xml_element(output_type, element):
    """Generates an object of the desired output type from an element in an XML ElementTree.

    Parameters
    ----------
    output_type : Type[OutputType]
        The type of the object to be generated.
    element : Element
        The element in an XML ElementTree from which to generate the output object

    Returns
    -------
    output_object : OutputType
        The generated object.
    """

    if element is None:
        return None

    if hasattr(output_type, "__args__"):
        base_output_type = output_type.__args__[0]
    else:
        base_output_type = output_type

    # If the desired type is not one of the XML object types, simply read in the value from the element
    if base_output_type not in S_XML_OBJECT_TYPES:
        try:
            constructor = get_constructor(base_output_type)
            return constructor(element.text)
        except Exception as e:
            logger.warning("Could not convert value %s to type %s; will be stored as a string. Exception was: %s",
                           element.text, base_output_type, e)
            return str(element.text)

    # We use the type's meta-info to find what attributes it has and their types, and use this to recursively
    # construct it
    d_attrs: Dict[str, Any] = {}
    attr_name: str
    dataclass_field: Field
    for attr_name, dataclass_field in base_output_type.__dataclass_fields__.items():

        attr_type = dataclass_field.type
        attr_tag: str = getattr(Tags, attr_name)

        # Special handling for lists
        if dataclass_field.default_factory == list:
            attr_elem_type = attr_type.__args__[0]

            l_sub_elements = recursive_element_find(element, attr_tag, find_all=True)
            d_attrs[attr_name] = [create_from_xml_element(attr_elem_type, sub_element)
                                  for sub_element in l_sub_elements]

        else:
            sub_element = recursive_element_find(element, attr_tag)
            d_attrs[attr_name] = create_from_xml_element(attr_type, sub_element)

    try:
        return base_output_type(**d_attrs)
    except Exception as e:
        print(str(e))


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

    root = tree.getroot()

    test_results = create_from_xml_element(TestResults, root)

    return test_results
