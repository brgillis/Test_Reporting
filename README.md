# OU-SHE Test Reporting

The published version of this project can be found at: http://bgilles.pages.euclid-sgs.uk/test_reporting/

---

This project hosts supporting documentation for the Software Test Plan/Report, including Testing Dataset definitions and
Software Problem Reports. It also automatically generates human-readable reports on validation test results.

## Table of Contents

* [Project Structure](#project-structure)
* [Publishing](#publishing)

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

GitBooks automatically compiles all Markdown (`*.md`) files in the `public` directory of this project into `.html` files
for web-based viewing, and deploys the compiled `.html` files and all other (non-`.md`) files from the `public`
directory to be publicly-viewable at the web address listed at the top of the document.

This project contains both a set of prepared `.md` files in its `public` directory, as well as a script (called as part
of the CI pipeline) which generates `.md` files to report on the results of validation tests. The set of test results to
generate reports for can be updated by adding or replacing the results tarballs in the `data` directory of this project 
and updating the `manifest.json` file.
