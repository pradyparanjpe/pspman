PSPMAN
------

**P**\ ersonal **S**\ imple **P**\ ackage **Man**\ ager (pspman) - a package manager aid

**P**\ ythonic **S**\ mall **P**\ ackage **Man**\ ager (pspman) - a package manager aid

DESCRIPTION
-----------

Manage git-cloned and installed packages.

Currently supports:
~~~~~~~~~~~~~~~~~~~

* python (pip)
* make (Makefile)
* meson (ninja)
* go
* `pull-only` (don't install)

Information
~~~~~~~~~~~

This is still only an *aid*. A lot of work still needs to be done manually.

Order of Operation
~~~~~~~~~~~~~~~~~~

* Delete projects
* Pull installation urls
* Update github projects

ENVIRONMENT
-----------

${HOME}/.pspman
~~~~~~~~~~~~~~~

Used as default ``prefix`` and parent for default clone directory ``programs``

CAUTION
-------

This is a `personal, simple` package manager. Do NOT run it as ROOT. Never supply root password or sudo prefix unless you really know what you are doing.

BUGS
----

May mess up root file system. Do not use as ROOT.
