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

Using bash script
^^^^^^^^^^^^^^^^^
-  copy installation script from `this <https://github.com/pradyparanjpe/pspman.git>`__ repository

.. code:: sh

   wget https://raw.githubusercontent.com/pradyparanjpe/pspman/master/install_scripts/install.sh

-  Run Installation script

.. code:: sh

   bash ./install.sh install

- Clean up: you may safely delete the installation script, and the aid script that it downloads

.. code:: sh

   rm ./install.sh ./_install.py

Using pip
^^^^^^^^^
- This option is described `just because` pspman is a python package.

- Create directories: ``${HOME}/.pspman``

.. code:: sh

   mkdir -p "${HOME}/.pspman/src" "${HOME}/.pspman/bin" "${HOME}/.pspman/lib"

-  install using pip

.. code:: sh

   pip install --prefix="${HOME}/.pspman" -U pspman

- arrange to export PYTHONPATH and PATH, Ex. by adding to ``${HOME}/.bashrc``:

.. code:: sh

   python_ver="$(python --version |cut -d "." -f1,2 |sed 's/ //' |sed 's/P/p/')"
   export PYTHONPATH="${HOME}/.pspman/lib/${python_version}/site-packages:${PYTHONPATH}"
   export PATH="${HOME}/.pspman/bin:${PATH}"

- Understand that `installation scripts` do precisely *the above* for you, in an organized way.


UNINSTALL
---------

Linux
~~~~~

.. _git-1:


Using bash script
^^^^^^^^^^^^^^^^^

-  Run (Un)Installation script

.. code:: sh

   cd "${HOME}/.pspman/src/pspman/install_scripts" && bash uninstall.sh

Using pip
^^^^^^^^^

.. _pip-1:


-  Remove using pip

.. code:: sh

   pip uninstall -y pspman

- Remove corresponding .bashrc configuration and ``${HOME}/.pspman`` folder


UPDATE
------

Linux
~~~~~

Using pspman
^^^^^^^^^^^^

(Use me to update myself): Run a regular update on the folder in which pspman is cloned

.. code:: sh

   pspman

`That's all!`

Using pip
^^^^^^^^^

.. code:: sh

    pip install --prefix="${HOME}/.pspman" -U pspman
