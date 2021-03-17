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


def install_make(code_path: str, prefix=str, argv: typing.List[str] = None,
                 env: typing.Dict[str, str] = None) -> bool:
    '''
    Install repository using `pip`

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    incl = os.path.join(prefix, 'include')
    libs = os.path.join(prefix, 'lib')
    include, library = (), ()
    if os.path.isdir(incl):
        include: typing.Tuple[str, str] = "-I", incl
    if os.path.isdir(libs):
        library: typing.Tuple[str, str] = "-I", libs
    configure = os.path.join(code_path, 'configure')
    argv, mod_env = prep_arg_env(argv, env)
    if os.path.exists(configure):
        conf_out = process_comm(configure, '--prefix', prefix, *argv,
                                env=mod_env, fail_handle='report')
        if conf_out is None:
            return False
    if os.path.isfile(os.path.join(code_path, './Makefile')):
        make_out = process_comm('make', *include, *library, incl, libs, '-C',
                                code_path, env=mod_env, fail_handle='report')
        if make_out is None:
            return False
        return bool(process_comm('make', *include, *library, '-C', code_path,
                                 'install', env=mod_env, fail_handle='report'))
    return False


def install_cmake(code_path: str, prefix=str, argv: typing.List[str] = None,
                env: typing.Dict[str, str] = None) -> bool:
    '''
    Install repository using `cmake`

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    argv, mod_env = prep_arg_env(argv, env)
    build_dir = os.path.join(prefix, 'temp_build', 'cmake')
    incl = os.path.join(prefix, 'include')
    libs = os.path.join(prefix, 'lib')
    include, library = (), ()
    if os.path.isdir(incl):
        include: typing.Tuple[str, str] = "-I", incl
    if os.path.isdir(libs):
        library: typing.Tuple[str, str] = "-I", libs
    os.makedirs(build_dir, exist_ok=True)

    # cmake build
    stdout = process_comm('cmake', '-D', f'CMAKE_INSTALL_PREFIX={prefix}',
                          '-B', build_dir, 'build', *argv, '-S', code_path,
                          fail_handle='report')
    if stdout is None:
        shutil.rmtree(build_dir)
        return False
    if not os.path.isfile(os.path.join(build_dir, 'Makefile')):
        shutil.rmtree(build_dir)
        return False
    make_pass = process_comm('make', *include, *library, '-C', build_dir,
                             env=mod_env, fail_handle='report')
    if make_pass is None:
        shutil.rmtree(build_dir)
        return False
    make_install = process_comm('make', *include, *library, '-C', build_dir,
                                'install', env=mod_env, fail_handle='report')
    shutil.rmtree(build_dir)
    return bool(make_install)



def install_pip(code_path: str, prefix=str, argv: typing.List[str] = None,
                env: typing.Dict[str, str] = None) -> bool:
    '''
    Install repository using `pip`

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    argv, mod_env = prep_arg_env(argv, env)
    requirements_file_path = os.path.join(code_path, 'requirements.txt')
    if os.path.exists(requirements_file_path):
        pip_req = process_comm('python3', '-m', 'pip', 'install', '--prefix',
                               prefix, '-U', '-r', requirements_file_path,
                               env=mod_env, fail_handle='report')
        if pip_req is None:
            return False
    return bool(process_comm('python3', '-m', 'pip', 'install', '--prefix',
                             prefix, '-U', *argv, code_path, env=mod_env,
                             fail_handle='report'))


def install_meson(code_path: str, prefix=str, argv: typing.List[str] = None,
                  env: typing.Dict[str, str] = None) -> bool:
    '''
    Install repository by building with `ninja/json`

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False`` if error/failure during installation, else, ``True``
    '''
    argv, mod_env = prep_arg_env(argv, env)
    subproject_dir = os.path.join(code_path, 'subprojects')
    os.makedirs(subproject_dir, exist_ok=True)
    _ = process_comm('pspman', '-c', subproject_dir, '-p', prefix,
                     env=mod_env, fail_handle='report')
    build_dir = os.path.join(prefix, 'temp_build', 'meson')
    os.makedirs(build_dir, exist_ok=True)
    build = process_comm('meson', '--buildtype=release', '--prefix', prefix,
                         *argv, '-Db_lto=true', build_dir, code_path,
                         env=mod_env, fail_handle='report')

    if build is None:
        shutil.rmtree(build_dir)
        return False
    meson_install = process_comm('meson', 'install', '-C', build_dir,
                                 env=mod_env, fail_handle='report')
    shutil.rmtree(build_dir)
    return bool(meson_install)


def install_go(code_path: str, prefix=str, argv: typing.List[str] = None,
               env: typing.Dict[str, str] = None) -> bool:
    '''
    Install repository using `pip`

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during installation
        env: Modifications in shell environment variables during installation

    Returns:
        ``False`` if error/failure during installation, else, ``True``

    '''
    argv, mod_env = prep_arg_env(argv, env)
    mod_env['GOROOT'] = prefix
    mod_env['GOPATH'] = prefix
    return bool(process_comm('go', 'install', '-i', *argv, '-pkgdir',
                             code_path, env=mod_env, fail_handle='report'))
