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
Automated Uninstallations

'''


import os
import typing
import shutil
from .shell import process_comm


def prep_arg_env(argv: typing.List[str] = None, env: typing.Dict[str, str]
                 = None) -> typing.Tuple[typing.List[str],
                                         typing.Dict[str, str]]:
    '''
    Process ``argv`` and ``env``

    Args:
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation
    '''
    argv = argv or []
    env = env or {}
    mod_env = os.environ.copy()
    for var, val in env.items():
        mod_env[var] = val
    return argv, mod_env


def remove_make(code_path: str, prefix=str, argv: typing.List[str] = None,
                 env: typing.Dict[str, str] = None) -> bool:
    '''
    Remove repository using `make`

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False`` if source-code can't be removed, else, ``True``

    '''
    incl = os.path.join(prefix, 'include')
    libs = os.path.join(prefix, 'lib')
    include: typing.Union[typing.Tuple[str, str], typing.Tuple] = ()
    library: typing.Union[typing.Tuple[str, str], typing.Tuple] = ()
    if os.path.isdir(incl):
        include = "-I", incl
    if os.path.isdir(libs):
        library = "-I", libs
    argv, mod_env = prep_arg_env(argv, env)
    if os.path.isfile(os.path.join(code_path, './Makefile')):
        return bool(process_comm('make', *include, *library, '-C', code_path,
                                 'uninstall', env=mod_env,
                                 fail_handle='report'))
    return False


def remove_cmake(code_path: str, prefix=str, argv: typing.List[str] = None,
                env: typing.Dict[str, str] = None) -> bool:
    '''
    Remove repository using `cmake`

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False`` if source-code can't be removed, else, ``True``

    '''
    argv, mod_env = prep_arg_env(argv, env)
    build_dir = os.path.join(prefix, 'temp_build', 'cmake')
    incl = os.path.join(prefix, 'include')
    libs = os.path.join(prefix, 'lib')
    include: typing.Union[typing.Tuple[str, str], typing.Tuple] = ()
    library: typing.Union[typing.Tuple[str, str], typing.Tuple] = ()
    if os.path.isdir(incl):
        include = "-I", incl
    if os.path.isdir(libs):
        library = "-I", libs
    os.makedirs(build_dir, exist_ok=True)

    # cmake build
    stdout = process_comm('cmake', '-D', f'CMAKE_REMOVE_PREFIX={prefix}',
                          '-B', build_dir, 'build', *argv, '-S', code_path,
                          fail_handle='report')
    if stdout is None:
        shutil.rmtree(build_dir)
        return False
    if not os.path.isfile(os.path.join(build_dir, 'Makefile')):
        shutil.rmtree(build_dir)
        return False
    make_remove = process_comm('make', *include, *library, '-C', build_dir,
                               'uninstall', env=mod_env, fail_handle='report')
    shutil.rmtree(build_dir)
    return bool(make_remove)



def remove_pip(code_path: str, prefix=str, argv: typing.List[str] = None,
                env: typing.Dict[str, str] = None) -> bool:
    '''
    Remove repository using `pip`.
    This may also affect --user's installation.

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False`` if source-code can't be removed, else, ``True``

    '''
    argv, mod_env = prep_arg_env(argv, env)
    name = os.path.split(code_path)[-1]
    return bool(process_comm('python3', '-m', 'pip', 'uninstall', '-y', name,
                             env=mod_env, fail_handle='report'))


def remove_meson(code_path: str, prefix=str, argv: typing.List[str] = None,
                  env: typing.Dict[str, str] = None) -> bool:
    '''
    Remove repository by building with `ninja/json`

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False`` if source-code can't be removed, else, ``True``
    '''
    argv, mod_env = prep_arg_env(argv, env)
    subproject_dir = os.path.join(code_path, 'subprojects')
    os.makedirs(subproject_dir, exist_ok=True)

    build_dir = os.path.join(prefix, 'temp_build', 'meson')
    os.makedirs(build_dir, exist_ok=True)
    build = process_comm('meson', '--buildtype=release', '--prefix', prefix,
                         *argv, '-Db_lto=true', build_dir, code_path,
                         env=mod_env, fail_handle='report')

    if build is None:
        shutil.rmtree(build_dir)
        return False
    meson_remove = process_comm('meson', 'uninstall', '-C', build_dir,
                                env=mod_env, fail_handle='report')
    shutil.rmtree(build_dir)
    return bool(meson_remove)


def remove_go(code_path: str, prefix=str, argv: typing.List[str] = None,
               env: typing.Dict[str, str] = None) -> bool:
    '''
    Remove repository using `go`
    This will always fail, since go uninstall recipe is not implemented.

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False``

    '''
    argv, mod_env = prep_arg_env(argv, env)
    return False
