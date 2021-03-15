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
import typing
from .shell import process_comm


def install_make(code_path: str, prefix=str, argv: typing.List[str] = None,
                 env: typing.Dict[str, str] = None) -> bool:
    '''
    Install repository using `pip`

    Args:
        code_path: path to to source-code
        prefix: ``--prefix`` flag value to be supplied

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    argv = argv or []
    env = env or {}
    incl = '-I' + os.path.join(prefix, 'include')
    libs = '-L' + os.path.join(prefix, 'lib')
    mod_env = os.environ.copy()
    for var, val in env.items():
        mod_env[var] = val
    configure = os.path.join(code_path, 'configure')
    makefile = os.path.join(code_path, 'Makefile')
    if os.path.exists(configure):
        conf_out = process_comm(configure, '--prefix', prefix, *argv,
                                env=mod_env,
                                fail_handle='report')
        if conf_out is None:
            return False
    if os.path.exists('./Makefile'):
        make_out = process_comm('make', incl, libs,
                                '-C', makefile, env=mod_env,
                                fail_handle='report')
        if make_out is None:
            return False
        return bool(process_comm('make', incl, libs,
                                '-C', makefile, 'install',
                                env=mod_env, fail_handle='report'))
    return False


def install_pip(code_path: str, prefix=str, argv: typing.List[str] = None,
                env: typing.Dict[str, str] = None) -> bool:
    '''
    Install repository using `pip`

    Args:
        code_path: path to to source-code
        prefix: ``--prefix`` flag value to be supplied

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    argv = argv or []
    env = env or {}
    mod_env = os.environ.copy()
    for var, val in env.items():
        mod_env[var] = val
    requirements_file_path = os.path.join(code_path, 'requirements.txt')
    if os.path.exists(requirements_file_path):
        pip_req = process_comm(
            'python3', '-m', 'pip', 'install', '--prefix', prefix, '-U', '-r',
            requirements_file_path, env=mod_env, fail_handle='report')
        if pip_req is None:
            return False
    return bool(process_comm(
        'python3', '-m', 'pip', 'install', '--prefix', prefix, '-U', *argv,
        code_path, env=mod_env, fail_handle='report'
    ))


def install_meson(code_path: str, prefix=str, argv: typing.List[str] = None,
                  env: typing.Dict[str, str] = None) -> bool:
    '''
    Install repository by building with `ninja/json`

    Args:
        code_path: path to to source-code
        prefix: ``--prefix`` flag value to be supplied

    Returns:
        ``False`` if error/failure during installation, else, ``True``
    '''
    argv = argv or []
    env = env or {}
    mod_env = os.environ.copy()
    for var, val in env.items():
        mod_env[var] = val
    update_dir = os.path.join(code_path, 'build', 'update')
    subproject_dir = os.path.join(code_path, 'subprojects')
    os.makedirs(subproject_dir, exist_ok=True)
    _ = process_comm('pspman', '-c', subproject_dir, '-p', prefix,
                     env=mod_env, fail_handle='report')
    os.makedirs(update_dir, exist_ok=True)
    build = process_comm('meson', '--wipe', '--buildtype=release',
                         '--prefix', prefix, *argv, '-Db_lto=true', update_dir,
                         code_path, env=mod_env, fail_handle='report')
    if build is None:
        build = process_comm(
            'meson', '--buildtype=release', '--prefix', prefix, *argv,
            '-Db_lto=true', update_dir, code_path,
            env=mod_env, fail_handle='report'
        )

    if build is None:
        return False
    return bool(process_comm(
        'meson', 'install', '-C', update_dir, env=mod_env, fail_handle='report'
    ))


def install_go(code_path: str, prefix=str, argv: typing.List[str] = None,
               env: typing.Dict[str, str] = None) -> bool:
    '''
    Install repository using `pip`

    Args:
        code_path: path to to source-code
        prefix: ``--prefix`` flag value to be supplied

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    argv = argv or []
    env = env or {}
    mod_env = os.environ.copy()
    for var, val in env.items():
        mod_env[var] = val
    mod_env['GOBIN'] = os.path.realpath(os.path.join(prefix, 'bin'))
    return bool(process_comm('go', 'install', '-i', '-pkgdir', *argv,
                            code_path, env=mod_env, fail_handle='report'))
