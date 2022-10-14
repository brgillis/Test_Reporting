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

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional


@dataclass
class Tags:
    """A special dataclass which defines the XML tags which we wish to read data from. The name of each attribute in
    this class corresponds to the name of the attribute in the associated dataclass which will store the information
    contained within that entry.
    """

    # Data stored in the AnalysisResult dataclass

    # Data stored in the RequirementResults dataclass

    # Data stored in the SingleTestResult dataclass
    test_id = "TestId"
    test_description = "TestDescription"
    global_result = "GlobalResult"
    l_requirements = "ValidatedRequirements"
    analysis_result = "AnalysisResult"

    # Data stored in the TestResultsMeta dataclass
    product_id = "ProductId"
    dataset_release = "DataSetRelease"
    plan_id = "PlanId"
    ppo_id = "PPOId"
    pipeline_definition_id = "PipelineDefinitionId"
    creation_date = "CreationDate"
    exp_product_id = "ExposureProductId"
    obs_id = "ObservationId"
    pnt_id = "PointingId"
    obs_mode = "ObservationMode"
    n_exp = "NumberExposures"
    tile_id = "TileId"
    source_pipeline = "SourcePipeline"

    # Data stored in the TestResults dataclass
    meta = ("Header", "Data")
    l_test_results = "ValidationTestList"


@dataclass
class AnalysisResult:
    pass


@dataclass
class RequirementResults:
    pass


@dataclass
class SingleTestResult:

    # Attributes specially added to the SHE implementation
    test_id: str
    test_description: str
    global_result: Literal["PASSED", "FAILED"]

    l_requirements: List[RequirementResults] = field(default_factory=list)
    analysis_result: Optional[AnalysisResult] = None


@dataclass
class TestResultsMeta:

    # Data stored in the header
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


@dataclass
class TestResults:
    meta: TestResultsMeta
    l_test_results: List[SingleTestResult] = field(default_factory=list)
    pass
