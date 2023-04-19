Legend
######

In the docs/tutorials, code examples are written as follows:

.. code-block::

   $ miracl -h

Code blocks look like this:

.. code-block::

   usage: miracl [-h] {connect,conv,flow,lbls,reg,seg,sta,stats,utils} ...

   positional arguments:
     {connect,conv,flow,lbls,reg,seg,sta,stats,utils}
       connect             connectivity functions
       conv                conversion functions
       flow                workflows to run
       lbls                label manipulation functions
       reg                 registration functions
       seg                 segmentation functions
       sta                 structure tensor analysis functions
       stats               statistical functions
       utils               utility functions
   
   optional arguments:
     -h, --help            show this help message and exit

Inline code is marked as: ``$ miracl -h``

Admonitions are displayed as colored text boxes. This is an example of what a 
'tip' admonition would look like:

.. tip::
   The above ``-h`` flag can be used with each of MIRACL's modules/functions

We use brackets to denote text as follows:

* ``{}``: Used for variabels.

  * Example: :file:`niftis/downsample\\{factor\\}x.nii.gz`

* ``<>``: Used for placeholder text in examples that you need to replace with your own information.
  
  * Example: ``$ ssh <username>@cedar.computecanada.ca``

* ``[ ]``: Placeholders for flag arguments used in command-line scripting.

  * Example: ``$ miracl flow sta -f [ Tiff folder ] -o [ output nifti ]``

* ``[]``: Denotes flags in the command-line help menus.
  
  * Example: ``$ miracl [-h]``

Files and directories (or generally paths) are denoted like this:
:file:`example_dir/example_file.nii.gz`

Names of exectutable programs are marked as follows: :program:`MIRACL`

Lastly, links are highlighted in blue (purple when clicked): 
`link to MIRACL's README 
<https://github.com/AICONSlab/MIRACL/blob/jo-docs_build_fix/README.md>`_
