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
from typing import Any, Dict, List, Literal, Optional, TypeVar
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


@dataclass
class Tags:
    """A special dataclass which defines the XML tags which we wish to read data from. The name of each attribute in
    this class corresponds to the name of the attribute in the associated dataclass which will store the information
    contained within that entry.
    """

    # Data stored in the AnalysisResult dataclass
    ana_result = "Result"
    textfiles_tarball = "AnalysisFiles.TextFiles.FileName"
    figures_tarball = "AnalysisFiles.Figures.FileName"
    ana_comment = "Comment"

    # Data stored in the RequirementResults dataclass
    req_id = "Id"
    meas_value = "MeasuredValue"
    req_result = "ValidationResult"
    req_comment = "Comment"
    supp_info = "SupplementaryInformation"

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
class AnalysisResult:
    ana_result: Literal["PASSED", "FAILED"]
    textfiles_tarball: Optional[str] = None
    figures_tarball: Optional[str] = None
    ana_comment: Optional[str] = None


@dataclass
class RequirementResults:
    req_id: str
    meas_value: Any
    req_result: Literal["PASSED", "FAILED"]
    req_comment: Optional[str] = None
    supp_info: Optional[str] = None


@dataclass
class SingleTestResult:

    # Attributes specially added to the SHE implementation
    test_id: str
    test_description: str
    global_result: Literal["PASSED", "FAILED"]

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


S_XML_OBJECT_TYPES = {TestResults, SingleTestResult, RequirementResults, AnalysisResult}

OutputType = TypeVar("OutputType")


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

    # If the desired type is not one of the XML object types, simply read in the value from the element
    if output_type not in S_XML_OBJECT_TYPES:
        return output_type(element.text)

    # We use the type's meta-info to find what attributes it has and their types, and use this to recursively
    # construct it
    d_attrs: Dict[str, Any] = {}
    attr_name: str
    dataclass_field: Field
    for attr_name, dataclass_field in output_type.__dataclass_fields__.items():

        attr_type = dataclass_field.type
        attr_tag: str = getattr(Tags, attr_name)

        # Special handling for lists
        if dataclass_field.default_factory == list:
            attr_elem_type = attr_type.__args__[0]

            l_sub_elements = element.findall(attr_tag)
            d_attrs[attr_name] = [create_from_xml_element(attr_elem_type, sub_element)
                                  for sub_element in l_sub_elements]

        else:
            d_attrs[attr_name] = element.find(attr_tag)

    return output_type(**d_attrs)


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
