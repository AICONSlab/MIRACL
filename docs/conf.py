# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "MIRACL"
copyright = "2025, Maged Goubran @ AICONS Lab"
author = "Maged Goubran"
# Version and release set to the same since no separation is needed
version = "2.5.1"
release = "2.5.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinxcontrib.mermaid",
    "sphinx_tabs.tabs",
    "sphinx_copybutton",
    "sphinxcontrib.email",
    "sphinx_contributors",
]

# Extension settings
# sphinx-copybutton
copybutton_prompt_text = "$ "  # Exclude '$' prompt when copying
copybutton_prompt_is_regexp = False  # Look for exact match of prompt text
copybutton_only_copy_prompt_lines = (
    True  # Only copy lines with code i.e. exlude outputs, comments etc.
)

# Disable source parser as only native .rst files are used
# Also deprecated since version 1.8. If you want to re-enable
# this use: Sphinx.add_source_parser()
# source_parsers = {
#    '.md': 'recommonmark.parser.CommonMarkParser',
# }

# The suffix(es) of source filenames
source_suffix = [".rst"]

# Add any paths that contain templates here, relative to this directory
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files. This pattern also
# affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The master toctree document
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use
pygments_style = "sphinx"

# Default is 'en' already but still better to set it explicitely
language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages. See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css"
html_static_path = ["_static"]

# Location of custom css file
html_css_files = [
    "css/custom.css",
]

# If true, “Created using Sphinx” is shown in the HTML footer.
# Default is True.
html_show_sphinx = False

# A dictionary of values to pass into the template engine's context for all
# pages. Single values can also be put in this dictionary using the '-A'
# command-line option of sphinx-build.
# Used here to add 'Edit on GitHub' to top right corner of documentation
html_context = {
    "display_github": True,
    "github_user": "AICONSlab",
    "github_repo": "MIRACL",
    "github_version": "master",
    "conf_py_path": "/docs/",
}

# Output file base name for HTML help builder.
htmlhelp_basename = "MIRACLdoc"

# -- Options for LaTeX output ------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "MIRACL.tex", "MIRACL Documentation", "Maged Goubran", "manual"),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "miracl", "MIRACL Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "MIRACL",
        "MIRACL Documentation",
        author,
        "MIRACL",
        "MIRACL is a general-purpose analysis pipeline",
        "Science",
    ),
]
