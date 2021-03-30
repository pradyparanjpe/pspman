##########
EXTENSIONS
##########

**(Advanced usage)**

PSPMan can be configured for any custom installation method.
It has been configured already for `make`, `cmake`, `pip`, and `meson`.
Instructions for installation are provided in an instruction-file described below.


*****************
Instruction File
*****************

Name
====
To supply installation instructions for a new method, create a file named `<method>`.yml.
e.g. `make`.yml, `cmake`.yml, `pip`.yml

Format
======
Instructions is in `yml` format, with :ref:`installation_variables` delimited by `dunders` (\ *__*\ )

PSPMan shall look for following yml objects in the instruction file:


Essential objects
------------------

* ``identifiers`` (list)— file or directory names, which, if present in the project folder,
  indicate that <method> can be used to install the project. e.g. `Makefile`, `configure`, `setup.cfg`

* ``install`` (str)— command that installs the project

  .. warning::
     Installation is *not* called from the project's source-directory. Suitable flags should be supplied
     to install the project from a given source or to build the project in a given build-directory.


Optional objects
-----------------

* ``commands`` (list)— required dependencies for installation. e.g. `make`, `gcc`
* ``env`` (dict)— "`key`: `value`" pairs; where `key` is a custom environment variable during installation.
* ``prepare`` (str)— Installation instruction
* ``build`` (str)— Installation instruction
* ``compile`` (str)— Installation instruction
* ``Uninstallation`` (str)— Uninstallation instruction.

.. _installation_variables:

Installation Variables
----------------------

Variables that are supplied by PSPMan for installation:

.. note::
   Not all of these need to be used in installation instructions.

* code_path (str)— path to source-code
* prefix (str)— install-prefix
* build_dir(str)— temporary directory to build source (this will get deleted during cleanup)
* library(str)— include libraries (gcc flag -L)
* include (list)— include libraries (gcc flag -I)
* argv (list)— args to be passed during installation,
    specified in modified installation URL (see USAGE documentation)


Order of Actions
================

For installation (or update): ``prepare`` → ``build`` → ``compile`` → ``install`` → (clean up builds)

For uninstallation: ``prepare`` → ``build`` → ``compile`` → ``uninstall`` → (clean up builds)

If any instruction is unavailable, its corresponding action is skipped.

Example
=======

.. code-block:: yaml
   :caption: cmake.yml
   :name: cmake.yml

      identifiers:
      - CMakeLists.txt
      commands:
      - cmake
      - make
      build: cmake -D CMAKE_INSTALL_PREFIX=__prefix__ -B __build_dir__ __argv__ build -S __code_path__
      install: make __include__ __library__ -C __build_dir__ install
      uninstall: make __include__ __library__ -C __build_dir__ uninstall
      env: {}
      # prepare:
      # compile:

Template
========

The template may be copied from PSPMan's source-code:

   `<pspman>/inst_config/template.yml`

OR here:

.. code-block:: yaml
   :caption: template.yml
   :name: template.yml

      identifiers: []  # unique files found in $codepath that identify install-type
      commands: []  # Required commands
      env: {}  # env.key: value forms
      # build:
      # compile:
      # install:
      # uninstall:

Locations
=========

Instruction-files are located and loaded in order from:

1. source-code (packaged-shipped): ``<prefix>/lib/python<X.Y>/site-packages/pspman/inst_config/<method>.yml``

   <prefix> is:

     * For self-managed installation of PSPMan:
       ``${HOME}/.local/share/pspman``

     * For pip-installed, -managed PSPMan:
       ``${HOME}/.local``

   .. warning::
      Files at this location should not be altered


2. pspman standard configuration directory: ``${XDG_CONFIG_HOME}/pspman/inst_config/<method>.yml``

   If ``${XDG_CONFIG_HOME}`` is not defined, ``${HOME}/.config`` is used.
   User-defined instruction-files should be placed/managed from here.

   .. Note::
      Remember to run ``pspman init`` script after each newly created instruction-file


Later instructions supersede earlier ones.
