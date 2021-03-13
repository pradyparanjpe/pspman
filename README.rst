PSPMAN
------

**PS**\ eudo **P**\ ackage **Man**\ ager (pspman) - a package manager aid

DESCRIPTION
-----------

Manage git-cloned and installed packages.

Documentation
-------------

|Documentation Status|

Source Code
-----------

|source| `Repository <https://github.com/pradyparanjpe/pspman.git>`__


Currently supports:
~~~~~~~~~~~~~~~~~~~

* python (pip)
* make (Makefile)
* meson (ninja)
* go
* `pull-only` (don't install)

Information
~~~~~~~~~~~

This is still only an *aid*. A lot of work needs to be done manually.

Order of Operation
~~~~~~~~~~~~~~~~~~

* Delete projects
* Pull installation urls
* Update github projects

ENVIRONMENT
-----------

${HOME}/.pspman
~~~~~~~~~~~~~~~

Used as default ``prefix`` and parent for default clone directory ``src``

CAUTION
-------

This is a `personal, simple` package manager. Do NOT run it as ROOT.
Never supply root password or sudo prefix unless you really know what you are doing.

BUGS
----

May mess up root file system. Do not use as ROOT.

.. |Documentation Status| image:: https://readthedocs.org/projects/pspman/badge/?version=latest
   :target: https://pspman.readthedocs.io/?badge=latest
.. |source| image:: https://github.githubassets.com/favicons/favicon.png
   :target: https://github.com/pradyparanjpe/pspman.git
