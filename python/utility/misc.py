"""
:file: utility/misc.py

:date: 10/18/2022
:author: Bryan Gillis

Module for miscellaneous utility functions used in this project.
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

import codecs
import hashlib
import logging
import re
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from typing import Callable  # noqa F401

logger = logging.getLogger(__name__)


def log_entry_exit(logger, level=logging.DEBUG):
    """Decorator which, when applied to a function, will log upon entry/exit of the function the name of the
    function, the arguments provided to it, and the output of it.

    Parameters
    ----------
    logger : Logger
        The logger to use for logging the info about this function.
    level : int, default=logging.DEBUG
        The level at which to log. Default: DEBUG

    Returns
    -------
    Callable
    """

    def func_wrap(func):
        def wrap(*args, **kwargs):
            logger.log(level, "Entering method `%s` with positional arguments `%s` and keyword arguments `%s`.",
                       func.__qualname__, args, kwargs)
            output = func(*args, **kwargs)
            logger.log(level, "Exiting method `%s` with output `%s`.", func.__qualname__, output)

            return output

        return wrap

    return func_wrap


@log_entry_exit(logger)
def extract_tarball(qualified_results_tarball_filename, qualified_tmpdir):
    """Extracts a tarball into the provided directory, performing security checks on the provided filename to ensure
    it doesn't contain any characters which are potentially unsafe in a `tar` command.

    Parameters
    ----------
    qualified_results_tarball_filename : str
        The fully-qualified filename of a tarball containing the test results product and associated datafiles.
    qualified_tmpdir : str
        The fully-qualified path to a temporary directory which can be used for this function.
    """

    # Silently coerce the input to strings
    qualified_results_tarball_filename = str(qualified_results_tarball_filename)
    qualified_tmpdir = str(qualified_tmpdir)

    # Check the filename contains only expected characters. If it doesn't, this could open a security hole
    filename_regex_match = re.match(r"^[a-zA-Z0-9\-_./+]*\.tar(\.gz)?$", qualified_results_tarball_filename)

    if not filename_regex_match:
        raise ValueError(f"Qualified filename {qualified_results_tarball_filename} failed security check. It must"
                         f"contain only alphanumeric characters and [-_./+], and must end with .tar or .tar.gz.")

    # Ditto for the directory being used
    tmpdir_regex_match = re.match(r"^[a-zA-Z0-9\-_./+]*?$", qualified_tmpdir)

    if not tmpdir_regex_match:
        raise ValueError(f"Qualified tempdir {qualified_tmpdir} failed security check. It must"
                         f"contain only alphanumeric characters and [-_./+].")

    cmd = f"cd {qualified_tmpdir} && tar -xf {qualified_results_tarball_filename}"
    tar_results = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if tar_results.returncode:
        if "No such file" in str(tar_results.stderr):
            raise FileNotFoundError(tar_results.stderr)
        raise ValueError(f"Un-tarring of {qualified_results_tarball_filename} failed. stderr from tar "
                         f"process was: {tar_results.stderr}")


@log_entry_exit(logger)
def hash_any(obj, max_length=None):
    """Hashes any immutable object into a base64 string of a given length.

    Parameters
    ----------
    obj : Any immutable
        The object to be hashed.
    max_length : int or None, default=None
        This limits the maximum length of the string to return. If None (default), the full hash will be returned.

    Returns
    -------
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