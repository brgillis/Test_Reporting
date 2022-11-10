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
* `public/` - Directory containing prepared Mardown and other files to be published
* `python/` - Directory containing Python code used for the generation of test reports
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
