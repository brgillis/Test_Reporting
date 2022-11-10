# OU-SHE Test Reporting

The published version of this project can be found at: http://bgilles.pages.euclid-sgs.uk/test_reporting/

---

This project hosts supporting documentation for the Software Test Plan/Report, including Testing Dataset definitions and
Software Problem Reports. It also automatically generates human-readable reports on validation test results.

## Table of Contents

* [Project Structure](#project-structure)
* [Publishing](#publishing)
* [Continuous Integration](#continuous-integration)
  * [`pytest` Job](#pytest-job)
  * [`build` Job](#build-job)
  * [`pages` Job](#pages-job)
  * [`pages-test` Job](#pages-test-job)

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
  * `python/implementations.py` - Python module which details which specialized implementations of building test reports
    are to be used on which files in the `manifest.json` file
* `test_data/` - Directory containing data used in unit tests of Python code
* `tests/` - Directory containing unit tests of Python code
* `.gitignore` - Standard .gitignore file to list files excluded from version control
* `manifest.json` - JSON-format manifest file, listing filenames of tarballs in the `data` directory (relative to that
  directory) for which test reports are to be generated
* `README.md` - This file

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
