#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This le is part of pspman.
#
# pspman is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pspman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pspman.  If not, see <https://www.gnu.org/licenses/>.
#
'''
setup script
'''


from os import environ, makedirs
from os import sep as ossep
from shutil import copy
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install


LONG_DESCRIPTION = ""
for read_file in ("./LongDescription", "./README.md"):
    try:
        with open(read_file, 'r') as README_FILE:
            LONG_DESCRIPTION = README_FILE.read()
            break
    except FileNotFoundError:
        continue


def mandb() -> None:
    '''
    copy man.db to ${HOME}/.local/share/man/man1/.
    '''
    man_dest = Path(environ["HOME"], '.local', 'share', 'man', 'man1')
    makedirs(man_dest, exist_ok=True)
    copy("pspman.1", man_dest)
    myhome = Path(environ["HOME"], ".pspman")
    makedirs(myhome, exist_ok=True)
    for workdir in ("bin", "share", "lib", "lib64",
                    "etc", "include", "tmp", "programs"):
        makedirs(myhome.joinpath(workdir), exist_ok=True)
    if "pspman" not in environ["PATH"]:
        with open(environ["HOME"] + ossep + ".bashrc", "a") as bash_f_h:
            print('export PATH="${PATH}:${HOME}/.pspman/bin"', file=bash_f_h, pad=True)


class PostDevelopCommand(install):
    """Post-installation for installation mode."""
    def run(self) -> None:
        '''
        run post install
        '''
        develop.run(self)
        mandb()


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self) -> None:
        '''
        run post install
        '''
        install.run(self)
        mandb()


setup(
    name='pspman',
    version='0.0.0.0.dev6',
    description="Personal Simple Package Manager",
    license="GPLv3",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Pradyumna Paranjape',
    author_email='pradyparanjpe@rediffmail.com',
    url="https://github.com/pradyparanjpe/pspman.git",
    packages=find_packages(),
    install_requires=['psprint'],
    scripts=['bin/pspman', ],
    package_data={},
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand
    }
)
