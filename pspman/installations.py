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
Automated installations

'''


import os
from .shell import process_comm


def install_make(code_path: str, prefix=str) -> bool:
    '''
    Install repository using `pip`

    Args:
        code_path: path to to source-code
        prefix: ``--prefix`` flag value to be supplied

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    configure = os.path.join(code_path, 'configure')
    makefile = os.path.join(code_path, 'Makefile')
    if os.path.exists(configure):
        conf_out = process_comm(configure, '--prefix', prefix,
                                fail_handle='report')
        if conf_out is not None:
            if os.path.exists('./Makefile'):
                make_out = process_comm('make', '-C', makefile,
                                        fail_handle='report')
                if make_out is not None:
                    return not(process_comm('make', '-C', makefile,
                                            'install', fail_handle='report'))
    return False


def install_pip(code_path: str, prefix=str) -> bool:
    '''
    Install repository using `pip`

    Args:
        code_path: path to to source-code
        prefix: ``--prefix`` flag value to be supplied

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    requirements_file_path = os.path.join(code_path, 'requirements.txt')
    if os.path.exists(requirements_file_path):
        pip_req = process_comm(
            'python', '-m', 'pip', 'install', '-U', '--user', '-r',
            requirements_file_path, fail_handle='report')
        if pip_req is None:
            return False
    return not(process_comm(
        'python', '-m', 'pip', 'install', '--user', '-U',
        code_path, fail_handle='report'
    ))


def install_meson(code_path: str, prefix=str) -> bool:
    '''
    Install repository by building with `ninja/json`

    Args:
        code_path: path to to source-code
        prefix: ``--prefix`` flag value to be supplied

    Returns:
        ``False`` if error/failure during installation, else, ``True``
    '''
    update_dir = os.path.join(code_path, 'build', 'update')
    subproject_dir = os.path.join(code_path, 'subprojects')
    os.makedirs(subproject_dir, exist_ok=True)
    _ = process_comm('pspman', '-c', subproject_dir,
                     fail_handle='report')
    os.makedirs(update_dir, exist_ok=True)
    build = process_comm('meson', '--wipe', '--buildtype=release',
                         '--prefix', prefix, '-Db_lto=true', update_dir,
                         code_path, fail_handle='report')
    if build is None:
        build = process_comm(
            'meson', '--buildtype=release', '--prefix', prefix,
            '-Db_lto=true', update_dir, code_path, fail_handle='report'
        )

    if build is None:
        return False
    return not(process_comm(
        'meson', 'install', '-C', update_dir, fail_handle='report'
    ))


def install_go(code_path: str, prefix=str) -> bool:
    '''
    Install repository using `pip`

    Args:
        code_path: path to to source-code
        prefix: ``--prefix`` flag value to be supplied

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    myenv = os.environ.copy()
    myenv['GOBIN'] = os.path.realpath(os.path.join(prefix, 'bin'))
    return not(process_comm('go', 'install', '-i', '-pkgdir',
                            code_path, fail_handle='report'))
