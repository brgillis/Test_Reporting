"""
:file: Test_Reporting/specialization_keys.py

:date: 11/04/2022
:author: Bryan Gillis

This python module defines implementations of building test reports for specific validation tests and for the default
case where no specific implementation is defined.

Instructions
------------

To define a new implementation, the following is the recommended procedure:

1. Choose a unique primary key (a lower-case string). This will be used in the manifest file to indicate the file for
   which this implementation should be used. This should be defined as a constant in the "Primary keys" section of this
   file, to allow easy changing of it in one place if desired in the future.

2. If there are multiple variants of this implementation, choose unique secondary keys for each of these and
   similarly define them as constants in a new "Secondary keys" section.

3. Define an implementation and import it to this file. This can most easily be an instance of the
   `ReportSummaryWriter` class or a child of it, but can also be any callable which share's the signature of its
   `__call__` method if desired. If using the `ReportSummaryWriter` class, see its documentation for instructions on
   how
   do define a new implementation.

4. In the definition of the `D_BUILD_CALLABLES` dict in this module, add an entry with the chosen primary key and
   implementation.

5. Add appropriate unit tests of all added functionality, including extending existing tests as appropriate.
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

from typing import Dict, Optional, TYPE_CHECKING

from Test_Reporting.specializations.cti_gal import CtiGalReportSummaryWriter
from Test_Reporting.specializations.dataproc import DataProcReportSummaryWriter
from Test_Reporting.specializations.galinfo import GalInfoReportSummaryWriter
from Test_Reporting.specializations.shear_bias import ShearBiasReportSummaryWriter
from Test_Reporting.utility.misc import logger
from Test_Reporting.utility.report_writing import BUILD_CALLABLE_TYPE, ReportSummaryWriter

if TYPE_CHECKING:
    from Test_Reporting.utility.report_writing import BUILD_CALLABLE_TYPE  # noqa F401

# Primary keys and aliases
CTI_GAL_KEY = "cti_gal"
CTI_GAL_KEY_ALIASES = ["cti-gal", "ctigal", "cti"]

SHEAR_BIAS_KEY = "shear_bias"
SHEAR_BIAS_KEY_ALIASES = ["shearbias", "sb"]

DATA_PROC_KEY = "dataproc"
DATA_PROC_KEY_ALIASES = ["data_proc", "data-proc", "dp"]

GAL_INFO_KEY = "galinfo"
GAL_INFO_KEY_ALIASES = ["gal_info", "gal-info", "gi"]

# Secondary keys for the CTI-Gal test case
OBS_KEY = "obs"
EXP_KEY = "exp"

# The build functions assigned to each key. The function assigned to the `None` key will be used if a key is used
# in the manifest which doesn't have a specific build function defined here
D_BUILD_CALLABLES: Dict[Optional[str], BUILD_CALLABLE_TYPE] = {}
for cti_gal_key in [CTI_GAL_KEY, *CTI_GAL_KEY_ALIASES]:
    D_BUILD_CALLABLES[cti_gal_key] = CtiGalReportSummaryWriter()
for shear_bias_key in [SHEAR_BIAS_KEY, *SHEAR_BIAS_KEY_ALIASES]:
    D_BUILD_CALLABLES[shear_bias_key] = ShearBiasReportSummaryWriter()
for dataproc_key in [DATA_PROC_KEY, *DATA_PROC_KEY_ALIASES]:
    D_BUILD_CALLABLES[dataproc_key] = DataProcReportSummaryWriter()
for galinfo_key in [GAL_INFO_KEY, *GAL_INFO_KEY_ALIASES]:
    D_BUILD_CALLABLES[galinfo_key] = GalInfoReportSummaryWriter()

DEFAULT_BUILD_CALLABLE = ReportSummaryWriter()


def determine_build_callable(key, value, raise_on_error=False) -> BUILD_CALLABLE_TYPE:
    """Uses user input for the build callable key (allowed values for which are specified in
    `specialization_keys.py`) and the target of it to determine the build callable to use. This handles checking for
    if `key` is None or the key is unrecognized and falls back to the default build callable, logging as appropriate.

    Note on the code - output type is specified here via Python's type-hinting syntax deliberately, due to it not being
    parsable in the docstring

    Parameters
    ----------
    key : str
        Case-insensitive key for the D_BUILD_CALLABLES dict, provided by the user as input.
    value : str or dict[str, str or None]
        The target on which the build callable is to be executed.
    raise_on_error : bool, default False
        If True, then if the key is unrecognized (and not None), a `ValueError` will be raised instead of logging an
        error.

    Returns
    -------
    build_callable : BUILD_CALLABLE_TYPE
        The determined build callable.
    """

    # Coerce the key to lower-case
    key = key.lower()
    build_callable = D_BUILD_CALLABLES.get(key)

    # Rather than using the default functionality of the dict's `get` method, we check explicitly, so we can log
    # in that case
    if not build_callable:
        if key is None:
            logger.info("No build callable key provided for data '%s'; using default implementation "
                        "%s to construct test report.", value, DEFAULT_BUILD_CALLABLE)
        elif raise_on_error:
            raise ValueError(f"No build callable available for key {key}. Allowed keys and associated build "
                             f"callables are: {D_BUILD_CALLABLES}.")
        else:
            logger.error("No build callable available for key '%s'; using default implementation "
                         "%s to construct test report from data: %s. Allowed keys and associated build "
                         "callables are: %s.", key, DEFAULT_BUILD_CALLABLE, value, D_BUILD_CALLABLES)
        build_callable = DEFAULT_BUILD_CALLABLE
    else:
        logger.info("Using build callable %s to construct test report from data: %s.", build_callable, value)

    return build_callable
