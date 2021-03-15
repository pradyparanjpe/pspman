
**PS**\ eudo **P**\ ackage **Man**\ ager (pspman) - a package manager aid

Documentation
-------------

|Documentation Status|

Source Code
-----------

|source| `Repository <https://github.com/pradyparanjpe/pspman.git>`__


DESCRIPTION
-----------

Manage:
    - automatically pull (update code)
    - group (maintain isolated groups)
    - attempt installation


Packages from Git Repositories.


Currently supports installation of:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    - python (pip)
    - make (Makefile)
    - meson (ninja)
    - go
    - `pull-only` (don't install)

Remember:
~~~~~~~~~

This is still only an *aid*. Some work
    - rebase
    - cherrypick
    - ediff
    - git headless state management
    - `etc.`

needs to be done manually.

Order of Operation
~~~~~~~~~~~~~~~~~~

* Delete projects (if requested)
* Pull installation urls (default)
* Update github projects

CAUTION
-------

This is a `personal` package manager. Do NOT run it as ROOT.

Never supply root password or sudo prefix unless you really know what you are doing.

BUGS
----

May mess up root file system. Do not use as ROOT.

.. |Documentation Status| image:: https://readthedocs.org/projects/pspman/badge/?version=latest
   :target: https://pspman.readthedocs.io/?badge=latest
.. |source| image:: https://github.githubassets.com/favicons/favicon.png
   :target: https://github.com/pradyparanjpe/pspman.git
