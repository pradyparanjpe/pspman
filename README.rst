******
PSPMAN
******

**PS**\ eudo **P**\ ackage **Man**\ ager (PSPMan) - a package manager aid

Source Code Repository
======================

|source| `Repository <https://github.com/pradyparanjpe/pspman.git>`__


Badges
======

|Documentation Status|  |PyPi Version|  |PyPi Format|  |PyPi Pyversion|


DESCRIPTION
===========

Manage:
    - automatically pull (update code)
    - group (maintain isolated groups)
    - attempt installation


Packages from Git Repositories.


Currently supports installation of:
-----------------------------------
    - python (pip)
    - make (configure, make)
    - make (Makefile)
    - cmake
    - meson (ninja)
    - `pull-only` (don't install)

May be extended for other methods using instruction file. (see documentation for Extensions)
Pull requests are welcome.

Remember:
---------

This is still only an *aid*. Some work
    - rebase
    - cherrypick
    - ediff
    - git headless state management
    - `etc.`

needs to be (/ can be) done manually.

All databases are deliberately maintained in yml format for a reason.


Order of Operation
------------------

* Delete projects (if requested)
* Pull installation urls (default)
* Update github projects

Installation
============

Refer to INSTALL.rst or Check section `INSTALLATION`

CAUTION
=======

This is a `personal` package manager. Do NOT run it as ROOT.

Never supply root password or sudo prefix unless you really know what you are doing.

BUGS
====

May mess up root file system. Do not use as ROOT.

``DEBUG``\ =\ ``True`` environment variable prints debugging information

.. |Documentation Status| image:: https://readthedocs.org/projects/pspman/badge/?version=latest
   :target: https://pspman.readthedocs.io/?badge=latest
.. |source| image:: https://github.githubassets.com/favicons/favicon.png
   :target: https://github.com/pradyparanjpe/pspman.git

.. |PyPi Version| image:: https://img.shields.io/pypi/v/pspman
   :target: https://pypi.org/project/pspman/
   :alt: PyPI - version

.. |PyPi Format| image:: https://img.shields.io/pypi/format/pspman
   :target: https://pypi.org/project/pspman/
   :alt: PyPI - format

.. |PyPi Pyversion| image:: https://img.shields.io/pypi/pyversions/pspman
   :target: https://pypi.org/project/pspman/
   :alt: PyPi - pyversion
