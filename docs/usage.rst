#####
USAGE
#####

Application
===========

-  Clone and install git projects.
-  Update existing git projects.
-  Try to install git projects using.

   -  ``configure``, ``make``, ``make install``.
   -  ``pip --user -U install .`` .
   -  meson/ninja.
   - go install
   - cmake build, ``make``, ``make install``

-  Delete cloned directories, try deleting installation files.
   [This may leave scars if the project does not have pre-programmed uninstallation routines]

Recommendation
--------------

Create similar/linked projects as GIT-Groups that update together (option ``-p``)


SYNOPSIS
========

.. argparse::
   :ref: pspman.define.cli
   :prog: pspman


EXAMPLES
========

- Show help

.. code:: sh

   pspman -h

- Update default location

.. code:: sh

   pspman

- Clone and install ``git@gitolite.local:foo.git``'s branch: devel

.. code:: sh

   pspman -i "git@gitolite.local/foo.git___devel"

- Delete package ``foo`` located in GIT-Group ``bar``

.. code:: sh

   pspman -d foo -p bar

- List projects in GIT-Group bar

.. code:: sh

   pspman -p bar list

- List known GIT-Groups

.. code:: sh

   pspman list --meta
