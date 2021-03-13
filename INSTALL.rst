PREREQUISITES
-------------

- `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`__
- `python3 <https://www.python.org/downloads/>`__
- `make <http://ftpmirror.gnu.org/make/>`__ (for ``make install``)
- `go <https://golang.org/doc/install>`__ (for ``go install``)
- `meson/ninja <https://mesonbuild.com/Getting-meson.html>`__ (for meson build, ninja install)

INSTALL
-------

Windows
~~~~~~~

Sorry

Apple
~~~~~

This App might not work for you, since you didn’t have to pay for it.
Also, it doesn't follow a `click-click-click done` approach. So, don't install it.

Linux
~~~~~

- REMEMBER, this is LGPLv3 (No warranty, your own risk, no guarantee of utility)

git
^^^

-  copy installation scripts from `this <https://github.com/pradyparanjpe/pspman.git>`__ repository

.. code:: sh

   wget https://github.com/pradyparanjpe/pspman/blob/master/install.sh
   wget https://github.com/pradyparanjpe/pspman/blob/master/install.py

-  Run Installation script

.. code:: sh

   bash ./install.sh install

pip
^^^

-  install using pip (Just because it is a python package)

.. code:: sh

   pip install --user -U pspman

- Create directories: ``${HOME}/.pspman``
- arrange to export PYTHONPATH and PATH, Ex. by adding to ``${HOME}/.bashrc``:

.. code:: sh

   export PYTHONPATH="${HOME}/.pspman/lib/``$python_version``/site-packages:${PYTHONPATH}"
   export PATH="${HOME}/.pspman/bin:${PYTHONPATH}"

- You will have to update the ``$python_version`` every time python is updated.

UNINSTALL
---------

.. _pip-1:

Linux
~~~~~

.. _git-1:

git
^^^

-  Run (Un)Installation script

.. code:: sh

   cd ${HOME}/.pspman/src/pspman && bash uninstall.sh

pip
^^^

-  Remove using pip

.. code:: sh

   pip uninstall -y pspman

- Remove corresponding configuration

UPDATE
------

Linux
~~~~~

git
^^^

(Use me to update myself): Run a regular update on the folder in which pspman is cloned

.. code:: sh

   pspman

`That's all!`

pip
^^^

.. code:: sh

    pip install -U pspman
