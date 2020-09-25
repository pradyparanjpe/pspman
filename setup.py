#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This le is part of pspman.
#
# pspman is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pspman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pspman.  If not, see <https://www.gnu.org/licenses/>.
#
'''
setup script
'''


from setuptools import setup


try:
    with open("./LongDescription", 'r') as README_FILE:
        LONG_DESCRIPTION = README_FILE.read()
except FileNotFoundError:
    LONG_DESCRIPTION = ""


setup(
    name='pspman',
    version='0.0.0.0dev1',
    description="Personal Simple Package Manager",
    license="GPLv3",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Pradyumna Paranjape',
    author_email='pradyparanjpe@rediffmail.com',
    url="https://github.com/pradyparanjpe",
    packages=['pspman'],
    install_requires=['colorama'],
    scripts=['bin/pspman', ],
    package_data={
    },
)