SYNOPSIS
--------

pspman -h

pspman [ -c DIR ] [ -p PREF ] [-f] [-o] [[-i URL] [-i URL]…] [[-d PROJ]
[-d PROJ]…]

Application
~~~~~~~~~~~~

-  Clone and install git projects.
-  Update existing git projects.
-  Try to install git projects using.

   -  ``configure``, ``make``, ``make install``.
   -  ``pip --user -U install .`` .
   -  meson/ninja.

-  Delete cloned directories [but not installation files]

Recommendation
~~~~~~~~~~~~~~

Create multiple Clone Directories (argument ``-c``) as package groups that update together.

OPTIONS
-------

-h, –-help
~~~~~~~~~~

View usage and help message

-c, –-clonedir DIR
~~~~~~~~~~~~~~~~~~

Path for all git clones [default:${HOME}/programs]

-p, –-prefix PREF
~~~~~~~~~~~~~~~~~

Path for installation [default:${HOME}]

-f, –-force-root
~~~~~~~~~~~~~~~~

Force working with root permission [DISCOURAGED]

-s, --stale
~~~~~~~~~~~

Skip updates, let the repository remain stale

-o, –-only-pull
~~~~~~~~~~~~~~~

Only pull, don’t try to install

-i, –-install URL
~~~~~~~~~~~~~~~~~

URL to clone new project

-d, -–delete PROJ
~~~~~~~~~~~~~~~~~

Delete PROJ

-l, --list-projs
~~~~~~~~~~~~~~~~

Display list of installed repositories and exit

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
