SYNOPSIS
--------

.. argparse::
   :ref: pspman.define.cli
   :prog: pspman


Application
-----------

-  Clone and install git projects.
-  Update existing git projects.
-  Try to install git projects using.

   -  ``configure``, ``make``, ``make install``.
   -  ``pip --user -U install .`` .
   -  meson/ninja.
   - go install

-  Delete cloned directories [but not installation files]

Recommendation
~~~~~~~~~~~~~~

Create multiple Clone Directories (argument ``-c``) as package groups that update together.

EXAMPLES
--------

Show help
~~~~~~~~~

.. code:: sh

   pspman -h

Update default locations
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   pspman

Clone and install ``git@gitolite.local:foo.git``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   pspman -i git@gitolite.local/foo.git

delete package ``foo`` located in directory ``bar``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: sh

   pspman -d foo -c bar
