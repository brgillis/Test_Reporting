# OU-SHE Test Reporting

The published version of this project can be found at: http://bgilles.pages.euclid-sgs.uk/test_reporting/

---

This project hosts supporting documentation for the Software Test Plan/Report, including Testing Dataset definitions and
Software Problem Reports. It also automatically generates human-readable reports on validation test results.


## Table of Contents

* [Contributors](#contributors)
  * [Active Contributors](#active-contributors)
  * [Other Contributors](#other-contributors)
* [Installation](#installation)
* [Executables](#executables)
  * [`build_all_report_pages.py`](#build_all_report_pagespy)
    * [Purpose](#purpose)
    * [Input](#input)
    * [Output](#output)
    * [Examples](#examples)
  * [`build_report.py`](#build_reportpy)
    * [Purpose](#purpose-1)
    * [Input](#input-1)
    * [Output](#output-1)
    * [Examples](#examples-1)
  * [`pack_results_tarball.py`](#pack_results_tarballpy)
    * [Purpose](#purpose-2)
    * [Input](#input-2)
    * [Output](#output-2)
    * [Examples](#examples-2)
* [Testing](#testing)
* [Project Structure](#project-structure)
* [Building Test Reports](#building-test-reports)
  * [Manifest](#manifest)
  * [Build Script](#build-script)
  * [Specialized Formatting](#specialized-formatting)
* [Publishing](#publishing)
* [Continuous Integration](#continuous-integration)
  * [`pytest` Job](#pytest-job)
  * [`install-test` Job](#install-test-job)
  * [`build` Job](#build-job)
  * [`pages` Job](#pages-job)
  * [`pages-test` Job](#pages-test-job)
* [Troubleshooting](#troubleshooting)
  * [A test failed when I ran `pytest`](#a-test-failed-when-i-ran-pytest)
  * [An exception was raised, what do I do?](#an-exception-was-raised-what-do-i-do)
  * [After updating or adding a results tarball, the `build` step fails](#after-updating-or-adding-a-results-tarball-the-build-step-fails)
  * [After adding a new specialized format, it isn't being used](#after-adding-a-new-specialized-format-it-isnt-being-used)
  * [The pipeline failed on master even though it succeeded on the feature branch](#the-pipeline-failed-on-master-even-though-it-succeeded-on-the-feature-branch)


## Contributors


### Active Contributors

* Bryan Gillis (b.gillis@roe.ac.uk)


### Other Contributors


## Installation

This project can be installed easily via Python's setuptools, by running the following command in the root directory:

```bash
python setup.py install --user
```

This installs the project into the user's `$HOME/.local/lib/python3.9/site-packages` directory, which must be added 
to the user's `PYTHONPATH` environment variable, and the executable scripts will be installed to their `$HOME/.
local/bin` directory, which must be added to the user's `PATH` environment variable. This can be done by e.g. adding 
this to their `.bash_profile` file:

```bash
export PYTHONPATH=PYTHONPATH:$HOME/.local/lib/python3.9/site-packages
export PATH=$PATH:$HOME/.local/bin
```

## Executables


### `build_all_report_pages.py`

**WARNING:** The script `build_all_report_pages.py` is intended for automatic execution as part of the
[Continuous Integration](#continuous-integration) pipeline. However, it can be run manually if desired for testing
purposes, though note that this will alter the contents of the project. This should only be done after committing any
work so that the changes can easily be rolled back.


#### Purpose

This script automatically generates reports on the validation test results contained in tarballs in the `data/`
directory of this project and listed in its `manifest.json` file. These reports will be stored in the `public/`
directory of this project and its subdirs, and some existing files in it will be updated to link to the newly-created
pages.


#### Input

This script takes the following parameters as input:

| **Argument**  | **Description**                                                                                              | **Required?** | **Default**                         |
|---------------|--------------------------------------------------------------------------------------------------------------|---------------|-------------------------------------|
| `--manifest`  | The manifest file (containing the filenames of tarballs in the `data/` directory to build reports on) to use | No            | `manifest.json`                     |
| `--rootdir`   | The root directory of this project                                                                           | No            | `os.path.cwd()` (Current directory) |
| `--log-level` | The level at which to log output (`DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`)                        | No            | `DEBUG`                             |

#### Output

This script creates the following output:

* Directory `<rootdir>/public/TR/`, containing the generated reports for each test
* Directory `<rootdir>/images/`, containing images referenced by the report
* Markdown file `<rootdir>/public/Test_Reports.md`, containing a table linking to all generated test reports

And modifies the following existing files:

* `<rootdir>/public/SUMMARY.md` is appended with links to all created Markdown files
* `<rootdir>/public/README.md` is appended with a Table of Contents linking to all other pages in the project (this will
  link to the expected `.html` filenames after being built by GitBooks, not the pre-compilation `.md` filenames)

This script also outputs a log of its execution via the standard Python logger, which outputs to stderr.


#### Examples

All arguments to the script allow default arguments, which are reasonable if running it from the project's root
directory on the included `manifest.json` file. Therefore, the script can be from this directory simply as:

```bash
build_all_report_pages.py
```

More generally, it can be run as:

```bash
build_all_report_pages.py [--manifest <manifest>] [--rootdir <rootdir>] [--logging-level <level>] 
```

with the proper paths to the desired manifest file and the project root directory and the desired logging level (e.g. 
DEBUG).

The script's execution log is output via stderr, and can be redirected to a file via e.g.:

```bash
build_all_report_pages.py 2> /path/to/build.log
```

When run as part of the [Continuous Integration](#continuous-integration) pipeline, this log is output to
`public/build.log`.


### `build_report.py`


#### Purpose

This script generates a report on the provided validation test results product or tarball. The generated report will be
in the format of multiple Markdown (`.md`) files, one for the test itself and one for each test case, and may also 
include references to images.


#### Input

This script takes the following parameters as input:

| **Argument**  | **Description**                                                                                                                                                                                                                                                                                                            | **Required?** | **Default**                         |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|-------------------------------------|
| `--target`    | The filename of either a tarball ("*.tar" or "*.tar.gz") of test results or a results data product ("*.xml"), for which reports should be built. If the latter is provided, data files it points to will be assumed to be in the "data" directory relative to it unless otherwise specified with the "--datadir" argument. | Yes           | N/A                                 |
| `--key`       | The key corresponding to the type of the results product, which can be used to invoke a specialized builder for it. The allowed values for this can be found in the module `python/specialization_keys.py`.                                                                                                                | No            | `None` (use the default builder)    |
| `--datadir`   | If the target is a results data product, this can be used to specify the directory that all data files it points to are relative to (this would be the "workdir" of the program which generated it).                                                                                                                       | No            | (Directory containing `target`)     |
| `--reportdir` | The directory in which to build the report pages.                                                                                                                                                                                                                                                                          | No            | `os.path.cwd()` (Current directory) |
| `--log-level` | The level at which to log output (`DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`)                                                                                                                                                                                                                                      | No            | `DEBUG`                             |

#### Output

This script creates the following output:

* Directory `<reportdir>/TR/`, containing the generated report for the test and its test cases
* Directory `<reportdir>/images/`, containing images referenced by the report

This script also outputs a log of its execution via the standard Python logger, which outputs to stderr.


#### Examples

Only the `target` argument needs to be supplied to this script; others all allow default arguments. So this can be run
most simply by e.g.

```bash
build_report.py /path/to/this/project/test_data/she_obs_cti_gal.tar.gz
```

More generally, it can be run as:

```bash
build_report.py <target> [--key <key>] [--datadir <datadir>] [--reportdir <reportdir>] [--logging-level <level>]
```

The script's execution log is output via stderr, and can be redirected to a file via e.g.:

```bash
build_report.py 2> ... /path/to/build.log
```


### `pack_results_tarball.py`


#### Purpose

This script packs one or more validation test results products, and all datafiles pointed to, into a tarball, to help
expedite the process of collecting new results and publishing them with this project.


#### Input

This script takes the following parameters as input:

| **Argument**  | **Description**                                                                                                                                                                                                                     | **Required?** | **Default**                                              |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|----------------------------------------------------------|
| `--target`    | The filename of either a `.xml` validation test results data product or a `.json` listfile of multiple such products. All products pointed to this way, plus all datafiles they point to, will be packed into a `.tar.gz` tarball." | Yes           | N/A                                                      |
| `--workdir`   | The directory which all provided filenames (including those referenced within listfiles and data products) are relative to.                                                                                                         | No            | (Directory containing `target`)                          |
| `--output`    | The desired filename of the tarball to be created.                                                                                                                                                                                  | No            | (Will use `target` with extension replaced by ".tar.gz") |
| `--log-level` | The level at which to log output (`DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`)                                                                                                                                               | No            | `DEBUG`                                                  |

#### Output

This script creates a single tarball as output. If the command-line argument `--output` is provided, this will be 
used as the name of this output file. Otherwise, it will be named based off of `target`, with the extension replaced 
by ".tar.gz"


#### Examples

Only the `target` argument needs to be supplied to this script; others all allow default arguments. So this can be run
most simply by e.g.

```bash
pack_results_tarball.py /path/to/this/project/test_data/she_observation_cti_gal_validation_test_results_product.xml
```

More generally, it can be run as:

```bash
pack_results_tarball.py <target> [--workdir <workdir>] [--output <output>] [--logging-level <level>]
```

The script's execution log is output via stderr, and can be redirected to a file via e.g.:

```bash
pack_results_tarball.py ... 2> /path/to/build.log
```


## Testing

This projects unit tests, along with a test build via GitBooks, are automatically run as part of the [Continuous
Integration](#continuous-integration) pipeline, and so this can be used to run tests and see the results after any
commit, without needing any extra setup.

Python unit tests can also be run manually if desired. This can be done most easily by adding the project's `python/`
directory to your `PYTHONPATH` and calling pytest on the `tests/` directory, i.e.:

```bash
PYTHONPATH=`pwd`/python pytest -v tests/
```


## Project Structure

* `data/` - Directory containing tarballs of validation tests results for which reports are to be automatically
  generated
* `public/` - Directory containing prepared Markdown and other files to be published
  * `public/images` - Directory containing images to be used in published files
  * `public/SPR` - Directory containing prepared Software Problem Report Markdown files to be published
  * `public/TD` - Directory containing prepared Testing Dataset Markdown files to be published
  * `public/README.md` - Markdown file which will be compiled into the front page of the published site
  * `public/SUMMARY.md` - Markdown file which will be compiled into the sidebar of the published site, linking to all
    pages in it (Note that any `.md` files not listed here will not be compiled into `.html` files)
* `python/Test_Reporting/` - Directory containing Python code used for the generation of test reports
  * `python/Test_Reporting/specializations/` - Python package containing code for specialized implementations of
    building test reports
  * `python/Test_Reporting/testing/` - Python package containing data and functionality used for unit testing
  * `python/Test_Reporting/utility/` - Python package containing modules providing needed functionality for building
    test reports
  * `python/Test_Reporting/build_all_report_pages.py` - Executable python script which is used as part of the Continuous
    Integration pipeline to build reports on test results tarballs
  * `python/Test_Reporting/build_report.py` - Executable python script which can be used to generate a report for a 
    test results product, without needing to add it to this project. 
  * `python/Test_Reporting/pack_results_tarball.py` - Executable python script which can be used to pack a test 
    results data product and all datafiles it points to into a tarball for easy copying into this project for 
    publication. 
  * `python/Test_Reporting/specialization_keys.py` - Python module which details which specialized implementations of
    building test reports are to be used on which files in the `manifest.json` file
* `test_data/` - Directory containing data used in unit tests of Python code
* `tests/` - Directory containing unit tests of Python code
* `.gitignore` - Standard .gitignore file to list files excluded from version control
* `manifest.json` - JSON-format manifest file, listing filenames of tarballs in the `data` directory (relative to that
  directory) for which test reports are to be generated
* `README.md` - This file


## Building Test Reports

As part of this project's [Continuous Integration](#continuous-integration) pipeline, it calls the
`python/Test_Reporting/build_all_report_pages.py` script to automatically generate test reports from tarballs of test results products
(and their associated data) in the `data/` directory of this project which are listed in the `manifest.json` file. This
section will provide an overview of files can be added and updated, and how to provide specialized implementations of
building test reports for tests where the default formatting is suboptimal.


### Manifest

The `manifest.json` file is a JSON-format file which lists the filenames of tarballs in the `data/` directory for which
test reports are to be generated. The files are stored in an `object` (similar to a Python dictionary), with each key
indicating the type of test, and, in the simplest case, the value being the tarball's filename relative to the `data/`
directory. For example:

```JSON
{
  "shear_bias": "shear_bias_test_results.tar.gz",
  "cti_psf": "cti_psf_test_results.tar.gz"
}
```

In this example, reports will be generated for two tests - `"shear_bias"` from the file
`data/shear_bias_test_results.tar.gz` and `"cti_psf"` from the file `cti_psf_test_results.tar.gz`. The key for each
of these tests will be used by the build script to determine if a [specialization](#specialized-formatting) is available
to build the test report. If so, this will be used, and if not, the test report will be built with the default
formatting.

In the case that you wish for multiple test reports to be generated for the same test, instead of providing a filename
directly, you can instead provide another object which uses as keys tags (which will be appended to the page names for the
generated reports) and as values the filenames of the test results tarballs, e.g.:

```JSON
{
  "cti_gal": {
    "obs": "cti_gal_obs_test_results.tar.gz",
    "exp-0": "cti_gal_exp_0_test_results.tar.gz",
    "exp-1": "cti_gal_exp_1_test_results.tar.gz",
    "exp-2": "cti_gal_exp_2_test_results.tar.gz",
    "exp-3": "cti_gal_exp_3_test_results.tar.gz"
  }
}
```

In this example, a test report will be generated for each of the files listed, with the title of each using the provided
tag, e.g. "CTI-Gal-obs" etc.


### Build Script

The script `python/Test_Reporting/build_all_report_pages.py` is used to automatically generate test reports from the
files listed in the `manifest.json` file and contained in the `data/` directory. It is not generally necessary to work
with this script directly when adding/updating test results tarballs or implementing new specialized formats.


### Specialized Formatting

The default formatting of test reports makes no assumption about the structure of the data contained within the test
results data product. As such, when the structure is known, it may be possible to more cleanly format the generated test
reports. For this purpose, this project allows extensions to its functionality to apply specialized formatting based on
the key used for each test in the [`manifest.json` file](#manifest).

To add a new specialization, two steps are necessary:

1. Create a new module in the `specializations` package which provides a function or callable object which can be used
   to generate a test report with the desired formatting. This is most easily done by making a child class of the
   `ReportSummaryWriter` class found in the `utility.test_writing` module and overriding methods as desired.
2. In the module `specialization_keys.py`, import the function or class created, and add an entry to the dict
   `D_BUILD_CALLABLES` associating the desired key for this test (e.g. "cti_gal") with the function or class instance,
   e.g.:

```python
from Test_Reporting.specializations.cti_gal import CtiGalReportSummaryWriter

CTI_GAL_KEY = "cti_gal"

D_BUILD_CALLABLES = {CTI_GAL_KEY: CtiGalReportSummaryWriter(), }
```

Further instructions can be found in the docstrings of the `ReportSummaryWriter` class in the `utility.test_writing`
module (for step 1) and the `specialization_keys` module.


## Publishing

This project is published via GitBooks, using GitLab's continuous integration pipeline. See the
[Continuous Integration](#continuous-integration) section of this document for more details on this pipeline.

GitBooks automatically compiles all Markdown (`*.md`) files in the `public/` directory of this project into `.html` files
for web-based viewing, and deploys the compiled `.html` files and all other (non-`.md`) files from the `public/`
directory to be publicly-viewable at the web address listed at the top of the document.

This project contains both a set of prepared `.md` files in its `public/` directory, as well as a script (called as part
of the CI pipeline) which generates `.md` files to report on the results of validation tests. The set of test results to
generate reports for can be updated by adding or replacing the results tarballs in the `data` directory of this project 
and updating the `manifest.json` file.


## Continuous Integration

This project uses GitLab's Continuous Integration functionality to automatically test the project, build test reports,
and publish via GitBooks with a pipeline which is run on every commit pushed to the remote repository. The control code
for this pipeline can be found in the `.gitlab-ci.yml` file in the root directory of this project.

The CI pipeline runs the following jobs in sequence, described in the sections below:

* `pytest`
* `install-test` (run in parallel with `pytest` job)
* `build`
* `pages` (only run on master branch) / `pages-test` (run on all other branches)

If any of these jobs fail, the pipeline will fail and no further jobs will be executed. This project is configured so
that the `master` branch can only be modified via Merge Request, and the pipeline must succeed for an MR to be merged.

### `pytest` Job

This job uses `pytest` to run all unit tests contained in the `tests/` directory of this project. If any of these tests
fail, the job fails.

### `install-test` Job

This job tests that this project can be successfully installed via setuptools.

### `build` Job

This job runs the `build_all_report_pages.py` script, which builds test reports for all tarballs in the `data/`
directory of this project which are listed in the `manifest.json` file. Syntax errors in the `manifest.json` file or
significant errors in the contents of a provided tarball may cause this job to fail. The script is able to recover from
some errors (such as figures referenced not being included in the tarball), however.

The log of running this script, including any errors it hit during execution, will be saved to the file
`public/build.log`, which will be saved as an artifact. 

### `pages` Job

This job is only run in the `master` branch of this project. It uses GitBooks to compile the prepared and built files.
See the [Publishing](#publishing) section for further details. The compiled files are stored in the `public/` directory,
which is saved as an artifact and deployed to be publicly-viewable at the address listed at the top of this document.

### `pages-test` Job

This job is run on all branches of this project except `master`. As with the [`pages` job](#pages-job), it uses Gitbooks
to compile the prepared and built files. This version, however, does not publish these files. It instead stores two
directories as artifacts:

* `test_input/` - This directory contains the Markdown and other files used as input for GitBooks. This includes the
  files created by the `build_all_report_pages.py` script
* `test_output/` - This contains the files compiled by GitBooks, which would be published if this branch were merged
  into the `master` branch

These artifacts can be found linked from the page for this job on GitLab, to either be downloaded or browsed. Note that
due to limitations of the browser, some links between published files may not work when browsed this way, even if they
will work when properly published.


## Troubleshooting

This section contains tips for resolving anticipated problems. If any problem occurs which isn't covered here, and you
cannot figure out the solution yourself, please contact the developers via raising an issue on this project's GitLab
page.


### A test failed when I ran `pytest`

This project's [Continuous Integration](#continuous-integration) pipeline is set up to ensure that no changes which
cause tests to fail will be merged to the `master` branch, so this issue will likely only occur due to changes in the
branch you're working. If you've made the changes yourself, investigate the details of the test failure and determine if
it indicates an issue with your code changes, or if the test needs to be updated to account for deliberately-changed
functionality.

If a test somehow does fail on the `master` branch, first check that you're running the latest version of it. Reset any
local changes and re-pull the `master` branch, and try running tests again. If the test still fails, check if it fails
in the CI pipeline run on GitLab. If it doesn't fail there, then likely indicates something on your system is the cause
of the difference (perhaps your `PYTHONPATH` is causing a clash). If it also fails there, then please report this issue
to the developers via a GitLab issue so that it can be fixed.


### An exception was raised, what do I do?

As with the previous section, we assume here that the CI pipeline will prevent this from occurring in the `master`
branch, and so assume here that this has occurred in your local branch due to some changes you've made.

_**Ensure you have the most up-to-date version of the project**_

It's possible the issue you're hitting is a bug that's already been fixed. Try pulling the `master` branch of the
project and merging it into your branch, and see if this fixes the issue.

_**See if the exception, traceback, or log gives you any other clue to solve the problem**_

There are many reasons something might go wrong, and many have been anticipated in the code with an exception to
indicate this. The exception text might tell you explicitly what the problem is - for instance, maybe two options you
set aren't compatible together. If it wasn't an anticipated problem, the exception text probably won't obviously
indicate the source of the problem, but you might be able to intuit it from the traceback. Look through the traceback at
least a few steps back to see if anything jumps out at you as a potential problem that you can fix. Also check the
logging of the program for any errors or warnings, and consider if those might be related to your problem.

_**Report the issue**_

If all else fails, raise an issue with the developers on GitLab. Be sure to include the following information:

1. Any details of input data you're using
2. The command you called to trigger the code
3. The full log of the execution, from the start of the program to the ultimate failure
4. Any steps you've taken to try to resolve this problem on your own


### After updating or adding a results tarball, the `build` step fails

First, check the build log for any indication of what went wrong. This can be found saved as an artifact by the `build`
step at `test_input/public/build.log`. This should give an indication of the cause of failure. You can also try running
the build manually with logging set to the DEBUG level to see if this helps you figure out what's going on.

In general, the most likely cause of this step failing is that the new results tarball contains data formatted in a way
that the build script is not expecting. The log should hopefully indicate where this issue occurred. If this is indeed
the case, the code will need to be updated to either handle this formatting or fail in a more graceful manner (logging
an error and outputting as much as it safely can). It is also possible that the data is corrupt in some way, in which
case the solution will be to fix the data, or else revert the changes if it cannot be fixed.


### After adding a new specialized format, it isn't being used

First, check that you've set up the format to be used for the desired test in the
`python/Test_Reporting/specialization_keys.py` file, and that the key used there matches the key used in the manifest
for the desired data.

If this is all set up correctly, it's possible that the code hit some issue in applying the specialized format and
gracefully fell back to the default format. This should be indicated in the log if this is the case, so check the log,
which will be stored as an artifact at `test_output/public/build.log` for any warnings or errors which might indicate
what went wrong.

If all else fails, try running the script yourself with a debugger and stepping through the code to see what happens.


### The pipeline failed on master even though it succeeded on the feature branch

Since the pipeline requires downloading the GitBooks package to install it, things can go wrong every once in a while.
Most likely this issue will resolve itself if you try re-running the pipeline.
