Code Documentation Standards for MIRACL
=======================================

All Python files used in MIRACL should adhere to the following documentation structure.
This guide aims to prioritizes readability, consistency, and maintainability over 
strict enforcement so please try to enforce these conventions but at your own discretion.

That said, I'm currently implemeting a cookiecutter create script function that should
be used to create the same scaffolding for any new script that is being created.

1. File Structure
-----------------
Files must be organized as follows:
   * Module-level Docstring (with :mod: references for important fns)
   * Imports (Standard Lib, then Third Party, then Local -> alphabetical within groups)
   * Optional code separators where it makes sense (e.g. long scripts, non-modular 
     code etc.)
   * Classes and Functions

This is partly at the discretion of the dev. For example, not every constant needs a
hearder section etc.

A note on separators: You should use ~80 characters for separators to maintain readability.
Separators can be:
   * Major sections: ``# ======= TITLE =======``
   * Minor sections: ``# ------- TITLE -------``

2. Docstring Format (Google Style)
----------------------------------
MIRACL uses the Google Python Style Guide for docstrings. The idea is that they are
easy to read for devs but that we can still use Sphinx syntax. I'm not a 100% sold on
this yet as I do like plain Sphinx and the Google Style also requires us to install
``sphinx.ext.Napoleon`` as yet another extension for Sphinx but let's use it for now.

Public and important functions must include:
   * **Summary:** A one-line description of what the function does.
   * **Args Section:** A list of all parameters, their types in parentheses, 
     and a description.
   * **Returns Section:** The type and description of the return value.
   * **Raises Section:** (If applicable) Any exceptions that are intentionally raised.
   * **Cross-References:** Use ``:mod:``, ``:func:``, or ``:class:`` to link 
     to related components. Links should mostly be used for non-obvious dependencies
     since we don't want the docstrings to become too brittle everytime there is a 
     refactor.
   * **Example:** Small example to make it easier to understand for new devs.

Short docstrings are okay for private helpers etc.

3. Type Hints
-------------
MIRACL scripts should be fully type annotated. At least public APIs must be.
No :prog:`mypy` integration yet but will hopefully be added in the future.

4. Linters/formatting/types
---------------------------
:prog:`MIRACL` uses ``ruff`` as its linter. ``mypy`` will hopefully be added in the 
future for type checking.

5. TYPE_CHECKING and __future__ Imports
---------------------------------------
When it makes sense, MIRACL should use ``typing.TYPE_CHECKING`` to handle imports that 
are only needed for type annotations.

This is useful to:
   * Avoid circular import issues.
   * Prevent heavy or unnecessary imports at runtime.
   * Maintain cleaner module boundaries.

Usage pattern:

.. code-block:: python

    from __future__ import annotations
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from miracl.models import BigModel

    def process(model: "BigModel") -> None:
        ...

Notes on this convention:
   * Imports inside ``if TYPE_CHECKING`` are ignored at runtime.
   * String annotations (e.g. ``"BigModel"``) should be used when referencing
     these types.
   * This pattern should be used when necessary, not by default.
   * Prefer standard imports unless there is a clear reason (e.g. circular dependency).
   * ``from __future__ import annotations`` is used for when we eventually migrate to 
     a more modern Python version. **MUST** always be the first import after the 
     docstring.

6. Notes
--------
Google Style rules:
   * Indentation matters: The description under Args: must be indented by 4 spaces.
   * The Colon: There is a colon after the argument name/type: name (type): description.
   * No blank lines between Args: Keep the arguments in a tight block, but put a blank line before the Returns: section.

:mod:`styleguide_template.rst` is the template that should be referenced for new scripts

7. To-do'
---------
* Add a error handling philosophy to this style guide.
