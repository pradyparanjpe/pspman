PREREQUISITES
=============

- `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`__
- `python3 <https://www.python.org/downloads/>`__
- `make <http://ftpmirror.gnu.org/make/>`__ (for ``make install``)
- `cmake <https://cmake.org/install/>`__ (for ``cmake build``)
- `go <https://golang.org/doc/install>`__ (for ``go install``)
- `meson/ninja <https://mesonbuild.com/Getting-meson.html>`__ (for meson build, ninja install)
- `bash <https://www.gnu.org/software/bash/>`__
    - Although ``pspman`` itself does not require `bash`, all exports (PATH, PYTHONPATH) are made for `bash`, which is a commonly used shell. If you use any other shell, you need to export PATH and PYTHONPATH. A pull request on `init <https://github.com/pradyparanjpe/pspman/blob/master/pspman/psp_in.py>`__ is welcome.

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
