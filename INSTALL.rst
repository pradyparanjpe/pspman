PREREQUISITES
=============

- `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`__
- `python3 <https://www.python.org/downloads/>`__
- `make <http://ftpmirror.gnu.org/make/>`__ (for ``make install``)
- `cmake <https://cmake.org/install/>`__ (for ``cmake build``)
- `meson/ninja <https://mesonbuild.com/Getting-meson.html>`__ (for meson build, ninja install)
- A POSIX compliant shell (sh, bash, ksh, tcsh, zsh, …).


INSTALL
=======

Windows
-------

Sorry


Apple
-----

This App might not work for you, since you didn’t have to pay for it.
Also, it doesn't follow a `click-click-click done` approach. So, don't install it.

Linux
-----

REMEMBER, this is LGPLv3 (No warranty, your own risk, no guarantee of utility)

-  install using `pip <https://pip.pypa.io/en/stable/installing/>`__

.. code:: sh

   pip install -U pspman

- run pspman init

.. code:: sh

   pspman init

.. note::
   Modifications tagged by ### PSPMAN_MOD ### will be written
   to ``${HOME}/.profile``, since it is the generic PROfile.
   If you are using `bash` (most likely) or `zsh` or any such
   POSIX shell, and any of its login profiles (``.bash_profile``,
   ``.bash_login``, ``.zlogin``, ``.zprofile``) exists, then,
   you need to suitably edit that login profile to inherit standard
   .profile, eg. by adding a line "``. "${HOME}"/.profile``".

   A reminder for this will be shown at init.

.. warning::
   If you are using a non-POSIX shell such as `fish` or `command-prompt`\ (!),
   PSPMan's init scripts won't care. You are responsible to locate and export
   pspman's standard prefix. (Generally present at
   ``${XDG_DATA_HOME:-${HOME}/.local/share}/pspman``)

   If you do not understand this warning, you probably aren't using one.

.. _recommended:

self-management
~~~~~~~~~~~~~~~

(optional, recommended)

.. code:: sh

   pspman -i "https://github.com/pradyparanjpe/pspman.git"


UNINSTALL
=========

Linux
-----

- Run pspman `goodbye`

.. code:: sh

   pspman goodbye


- Remove using ``pip``

.. code:: sh

   pip uninstall -y pspman


UPDATE
------

Linux
~~~~~

If :ref:`recommended` was opted, use me to update myself:

Run a regular update on the folder in which pspman is cloned

.. code:: sh

   pspman

`That's all!`

Using pip
^^^^^^^^^

.. code:: sh

    pip install -U pspman
