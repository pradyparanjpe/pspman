PREREQUISITES
-------------

-  git
-  python3

INSTALL
-------

Windows
~~~~~~~

Sorry

Apple Mac
~~~~~~~~~

This App might not work for you, since you didn’t have to pay for it.

Linux
~~~~~

git
^^^

-  copy from `this <https://github.com/pradyparanjpe/pspman.git>`__ repository

.. code:: sh

   wget https://github.com/pradyparanjpe/pspman/blob/master/install.sh
   wget https://github.com/pradyparanjpe/pspman/blob/master/install.py

-  Run Installation script

.. code:: sh

   bash ./install.sh install

pip
^^^

-  install using pip

.. code:: sh

   pip install --user -U pspman

- Create directories: ``${HOME}/.pspman``
- arrange to export PYTHONPATH and PATH, ex. by adding to ``${HOME}/bashrc``:

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

-  Run Installation script

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

(Use me to update myself) - Run a regular update on the folder in which
pspman is cloned

.. code:: sh

   pspman
