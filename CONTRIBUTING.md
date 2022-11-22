# Contribution Guidelines

## Table of Contents

* [Before Contributing](#before-contributing)
  * [Check if it's been proposed before](#check-if-its-been-proposed-before)
  * [Prepare your editor](#prepare-your-editor)
* [While Contributing](#while-contributing)
* [Submitting Contributions](#submitting-contributions)
* [Coding Style](#coding-style)
  * [Documentation](#documentation)
  * [Naming](#naming)
  * [IDE Support](#ide-support)
  * [Logging](#logging)

## Before Contributing

### Check if it's been proposed before

Check if your desired change has already been proposed by checking historical issues and merge requests.

If it's been previously proposed and rejected, generally you should not re-propose the same change barring 
exceptional circumstances.

If it's been proposed and is being worked on, consider offering to help with the existing proposal.

If it's been proposed and is awaiting review, and you're positioned to be able to review it, consider offering to do 
so.

### Prepare your editor

To ensure that all code and documentation follows the same format, it may be helpful to prepare your editor to 
automatically format to this project's style (see the [Coding Style](#coding-style) section below). If you've done 
this, try running an autoformatting pass on the codebase before making any changes. If you've set it up properly, this
should result in no changes. If it does change something, use this as an indication of what might need to be changed 
in your settings.

It is not necessary to use an autoformatter if you would prefer not to. In this case, remember to take care that all 
code you write matches this project's style.

If you're using an IDE, you'll need to set up project paths. In this project, the `python/` directory should be 
added to your `PYTHONPATH`. If your IDE supports unit testing, you can set it up to run the python unit tests in the 
`tests/` directory. Otherwise, you can take advantage of this project's Continuous Integration pipeline, which runs them
on every commit pushed to the remote repository.

## While Contributing

Create a new branch to work on with an appropriate name, branched off of the `master` branch.

Make whatever changes you desire, commit them, and push them. Check that the Continuous Integration pipeline passes 
regularly, and address any issues if it doesn't.

In deciding what changes to make, keep in mind that smaller Merge Requests are easier to review. It's fine to fix a few
minor unrelated issues you notice while working on the code (e.g. typos), but if you end up doing a lot of this, 
consider if it would be better to do this in a separate MR dedicated to this type of change.

If your work takes a significant amount of time, regularly pull the `master` branch of the project and merge it into
your branch to incorporate any changes from it. This may also need to be done while waiting for your MR to be reviewed.

## Submitting Contributions

Push all of your changes, and confirm that the Continuous Integration pipeline passes. Update the `CHANGELOG` file 
to note what changes you've made.

If you've already created a draft Merge Request for this change, mark it as ready and assign it for review. If not, 
create a Merge Request and assign it for review. The MR should clearly explain the purpose of the change. It should 
also include any other information that may be necessary to help the reviewer understand it.

Address any issues that arise in review.

## Coding Style

This project follows the [Euclid coding
standards](https://euclid.roe.ac.uk/projects/coding-standards/wiki/User_Cod_Std-pythonstandard-v1-1) except where
indicated otherwise. This includes standard PEP8 python formatting guidelines, with the exception that the maximum line
length is set to 120 characters instead of 80.

This projects also uses the following extensions to these coding standards:

### Documentation

All modules (including `__init__.py`s) should include a docstring at the top, followed by the Euclid copyright 
notice. See any existing file for the formats of these. The description portion of the module docstring may be a 
one-liner or more detailed as desired.

Any public function or class of more than trivial complexity should have a full, NumPy-style docstring. This should 
include full type information for both parameters and return values. The first time a parameter is documented in any 
given module should include a description of it. Any subsequent uses of it may omit the description.

Private or trivial functions and classes may use a one-liner docstring if desired. In this case, all parameters and 
return values should have type hints specified.

When variables are declared without their type being immediately obvious, type hinting should be used. E.g.:

```python
l_to_be_filled: List[str] = []
```

In this example, while this is obviously a list, the expected item type isn't obvious without type hinting.

### Naming

This project uses a limited amount of Apps Hungarian Notation to help indicate data structures. The following 
conventions are used:

* Lists, Tuples, and other Sequences: Variable name begins with `l_`, or constant name with `L_`. E.g.: `l_vals = [1, 
2]`, `L_CONST_VALS = (3, 4)`.
* Dicts and other Mappings: Variable name begins with `d_`, or constant name with `D_`. E.g.: `d_info = {"foo": 1, 
"bar": 2}`, `D_CONST_INFO = {"foo": 3, "bar": 4}`

The primary purpose of this is to ease readability, so that the user doesn't have trouble distinguishing at a glance 
e.g. `my_long_name_variable` and `my_long_name_variables`, where the latter is a list of the former.

### IDE Support

This project uses some conventions which are aimed at allowing IDEs to better interpret its code.

Any deliberate contravention of coding guidelines should be flagged as such by adding `  # noqa <number>`, were 
`<number>` is the number of the guideline being violated. E.g. `  # noqa F401` is used when importing something
which isn't used in a given module.

When a parameter or return value's type is only specified in a docstring and not used elsewhere in a module, IDEs may 
not be able to identify it and will treat it as `Any`. To rectify this, the type should be imported within a special 
`if TYPE_CHECKING:` block after the imports section, and flagged with `  # noqa F401`. E.g.:

```python
from typing import TYPE_CHECKING

import pytest

...

if TYPE_CHECKING:
    from _pytest.tmpdir import TempdirFactory  # noqa F401
    
...

@pytest.fixture
def project_copy(rootdir, tmpdir_factory):
    """Pytest fixture which creates a copy of the project in a temporary directory for use with unit testing.

    Parameters
    ----------
    rootdir : str
        Pytest fixture providing the root directory of the project.
    tmpdir_factory : TempdirFactory
        Pytest fixture providing a factory to create temporary directories for testing.

    Returns
    -------
    project_copy_rootdir : str
        The fully-qualified path to the created project copy
    """
```

This will allow IDEs to identify the type of this parameter when it's moused-over. Containing the import in this 
block is done to indicate to the reader that these imports are used only for type-checking, and so that the flag to 
ignore unused imports is applied only to these imports and not any other imports from the same module. The `  # noqa 
F401` flag is used to indicate to format-checker to ignore this line if they believe these imports are unused.

Take care to maintain this block if the imports are no longer needed, as this will not be caught by autoformatters.

### Logging

To aid in diagnosing issues, non-trivial functions within this project use the `log_entry_exit` decorator, which 
logs (at debug level by default) when the function is entered and exited, and with what arguments. This should be used 
as e.g.:

```python
from logging import getLogger

from Test_Reporting.utility.misc import log_entry_exit

logger = getLogger(__name__)

@log_entry_exit(logger)
def my_function():
    ...
```
