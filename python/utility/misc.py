"""
:file: utility/misc.py

:date: 10/12/2022
:author: Bryan Gillis

Module for miscellaneous utility functions.
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
import re
import subprocess


def extract_tarball(qualified_results_tarball_filename, qualified_tmpdir):
    """Extracts a tarball into the provided directory, performing security checks on the provided filename.

    Parameters
    ----------
    qualified_results_tarball_filename : str
        The fully-qualified filename of a tarball containing the test results product and associated datafiles
    qualified_tmpdir : str
        The fully-qualified path to a temporary directory which can be used for this function.
    """

    # Check the filename contains only expected characters. If it doesn't, this could open a security hole
    regex_match = re.match(r"^[a-zA-Z\-_./]*\.tar(\.gz)?$", qualified_results_tarball_filename)

    if not regex_match:
        raise ValueError(f"Qualified filename {qualified_results_tarball_filename} failed security check. It must"
                         f"contain only alphanumeric characters and [-_./], and must end with .tar or .tar.gz.")

    cmd = f"cd {qualified_tmpdir} && tar -xf {qualified_results_tarball_filename}"
    tar_results = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if tar_results.returncode:
        raise ValueError(f"Un-tarring of {qualified_results_tarball_filename} failed. stderr from tar "
                         f"process was: {tar_results.stderr}")


def hash_any(obj, max_length=None):
    """Hashes any immutable object into a base64 string of a given length.

    Parameters
    ----------
    obj : Any immutable
        The object to be hashed
    max_length : int
        This limits the maximum length of the string to return

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
