# OU-SHE Test Reporting

The published version of this project can be found at: http://bgilles.pages.euclid-sgs.uk/test_reporting/

---

This project hosts supporting documentation for the Software Test Plan/Report, including Testing Dataset definitions and
Software Problem Reports. It also automatically generates human-readable reports on validation test results.

## Table of Contents

* [Contributors](#contributors)
  * [Active Contributors](#active-contributors)
  * [Other Contributors](#other-contributors)
* [Project Structure](#project-structure)
* [Building Test Reports](#building-test-reports)
  * [Manifest](#manifest)
  * [Build Script](#build-script)
  * [Specialized Formatting](#specialized-formatting)
* [Publishing](#publishing)
* [Continuous Integration](#continuous-integration)
  * [`pytest` Job](#pytest-job)
  * [`build` Job](#build-job)
  * [`pages` Job](#pages-job)
  * [`pages-test` Job](#pages-test-job)

## Contributors

### Active Contributors

* Bryan Gillis (b.gillis@roe.ac.uk)

### Other Contributors

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
* `python/` - Directory containing Python code used for the generation of test reports
  * `python/specializations/` - Python package containing code for specialized implementations of building test reports
  * `python/testing/` - Python package containing data and functionality used for unit testing
  * `python/utility/` - Python package containing modules providing needed functionality for building test reports
  * `python/build_all_report_pages.py` - Executable python script which is used as part of the Continuous Integration
    pipeline to build reports on test results tarballs
  * `python/specialization_keys.py` - Python module which details which specialized implementations of building test reports
    are to be used on which files in the `manifest.json` file
* `test_data/` - Directory containing data used in unit tests of Python code
* `tests/` - Directory containing unit tests of Python code
* `.gitignore` - Standard .gitignore file to list files excluded from version control
* `manifest.json` - JSON-format manifest file, listing filenames of tarballs in the `data` directory (relative to that
  directory) for which test reports are to be generated
* `README.md` - This file

## Building Test Reports

As part of this project's [Continuous Integration](#continuous-integration) pipeline, it calls the
`python/build_all_report_pages.py` script to automatically generate test reports from tarballs of test results products
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

The script `python/build_all_report_pages.py` is used to automatically generate test reports from the files listed in
the `manifest.json` file and contained in the `data/` directory. It is not generally necessary to work with this script
directly when adding/updating test results tarballs or implementing new specialized formattings.

### Specialized Formatting

The default formatting of test reports makes no assumption about the structure of the data contained within the test
results data product. As such, when the structure is known, it may be possible to more cleanly format the generated test
reports. For this purpose, this project allows extensions to its functionality to apply specialized formatting based on
the key used for each test in the [`manifest.json` file](#manifest).

To add a new specialization, two steps are necessary:

1. Create a new module in the `specializations` package which provides a function or callable object which can be used
   to generate a test report with the desired formatting. This is most easily done by making a child class of the
   `TestSummaryWriter` class found in the `utility.test_writing` module and overriding methods as desired.
2. In the module `specialization_keys.py`, import the function or class created, and add an entry to the dict
   `D_BUILD_CALLABLES` associating the desired key for this test (e.g. "cti_gal") with the function or class instance,
   e.g.:

```python
from specializations.cti_gal import CtiGalTestSummaryWriter

CTI_GAL_KEY = "cti_gal"

D_BUILD_CALLABLES = {CTI_GAL_KEY: CtiGalTestSummaryWriter(), }
```

Further instructions can be found in the docstrings of the `TestSummaryWriter` class in the `utility.test_writing`
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
* `build`
* `pages` (only run on master branch) / `pages-test` (run on all other branches)

If any of these jobs fail, the pipeline will fail and no further jobs will be executed. This project is configured so
that the `master` branch can only be modified via Merge Request, and the pipeline must succeed for an MR to be merged.

### `pytest` Job

This job uses `pytest` to run all unit tests contained in the `tests/` directory of this project. If any of these tests
fail, the job fails.

### `build` Job

This job runs the `python/build_all_report_pages.py` script, which builds test reports for all tarballs in the `data/`
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
  files created by the `python/build_all_report_pages.py` script
* `test_output/` - This contains the files compiled by GitBooks, which would be published if this branch were merged
  into the `master` branch

These artifacts can be found linked from the page for this job on GitLab, to either be downloaded or browsed. Note that
due to limitations of the browser, some links between published files may not work when browsed this way, even if they
will work when properly published.
