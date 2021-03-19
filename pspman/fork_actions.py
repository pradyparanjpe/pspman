#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This le is part of pspman. #
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
Parallel multiprocessed operations

All `actions` accept same set of args and return same type of object

    Args:
        * env: action context
        * project: project on which action is requested

    Returns:
        * project.name for indexing
        * project.tag feedback to update parent
        * success code of action to inform parent

            * code == 1: Successfully modified
            * code == -1: Failed at action
            * code == 0: Nothing changed


'''


import os
import typing
import shutil
from . import print
from .shell import git_comm
from .classes import InstallEnv, GitProject
from .tag import ACTION_TAG, FAIL_TAG, TAG_ACTION, RET_CODE
from .installations import (install_make, install_pip,
                            install_meson, install_go, install_cmake)
from .uninstallations import (remove_make, remove_pip,
                              remove_meson, remove_go, remove_cmake)


def delete(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, int]:
    '''
    Delete this project

    Args:
        args:
            * env: installation context
            * project: project to delete

    Returns:
        project.name, project.tag, success code of action

    '''
    env, project = args
    print(f'''
    Removing {project.name}.

    This project may be added again using:
    pspman -i {project.url}
    ''', mark='delete' )
    inst_tag = project.tag & 0xf0
    if inst_tag:
        # Attempt uninstallation
        if env.verbose:
            print( f'''
            Trying standard uninstall calls with {TAG_ACTION[inst_tag]}.
            This may not always be clean; some scars may stay back.
            ''', mark='delete')

        remove_call: typing.Callable = {
            0x10: remove_make, 0x20: remove_pip, 0x30: remove_meson,
            0x40: remove_go, 0x80: remove_cmake
        }.get(inst_tag, lambda **_: True)
        success = remove_call(code_path=os.path.join(env.clone_dir,
                                                     project.name),
                              prefix=env.prefix, argv=project.inst_argv,
                              env=project.sh_env)
        if not success:
            if env.verbose:
                print(f'FAILED Uninstalling project {project.name}',
                      mark='fdelete')
                print(f'Proceeding to delete the source code anyway...',
                      mark='info')

    # Erase source code
    if env.verbose:
        print('Erasing source code', mark='delete')
    try:
        shutil.rmtree(os.path.join(env.clone_dir, project.name))
        return project.name, project.tag & (0xff - ACTION_TAG['delete']),\
            RET_CODE['pass']
    except OSError:
        print(f'Failed Deleting {project.name}', mark='fdelete')
        return project.name, project.tag, RET_CODE['fail']


def clone(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, int]:
    '''
    Get (clone) the remote project.url

    Args:
        args:
            * env: installation context
            * project: project to delete

    Returns:
        project.name, project.tag, success code of action

    '''
    env, project = args
    if project.url is None:
        print(f'URL for {project.name} was not supplied', mark='err')
        return project.name, project.tag, RET_CODE['fail']
    gitkwargs: typing.Dict[str, typing.Optional[str]] = {}
    if project.branch is not None:
        gitkwargs['branch'] = project.branch
    success = git_comm(clone_dir=os.path.join(env.clone_dir, project.name),
                       motive=(project.url, project.name), gitkwargs=gitkwargs)
    if success is None:
        # STDERR thrown
        print(f'Failed to clone source of {project.name}', mark='fclone')
        return (project.name, project.tag, RET_CODE['fail'])
    project.type_install(env=env)
    if env.verbose:
        print(f'{project.name} cloned', mark='clone')
    tag = (project.tag | ACTION_TAG['install']) & (0xff - ACTION_TAG['pull'])
    return project.name, tag, RET_CODE['pass']


def update(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, int]:
    '''
    Update (pull) source code.

    Args:
        args:
            * env: installation context
            * project: project to delete

    Returns:
        project.name, project.tag, success code of action

    '''
    env, project = args
    g_pull = git_comm(clone_dir=os.path.join(env.clone_dir, project.name),
                      motive='pull')
    if g_pull is not None:
        # STDERR from pull was blank
        tag = project.tag & (0xff - ACTION_TAG['pull'])
        if 'Already up to date' in g_pull:
            # Up to date
            if env.verbose:
                print(f'{project.name} is up to date.', mark='pull')
            return project.name, tag, RET_CODE['asis']
        if 'Updating ' in g_pull:
            # STDOUT mentioned that the project was updated in some way
            tag |= ACTION_TAG['install']
            if env.verbose:
                print(f'{project.name} was updated.', mark='pull')
            return project.name, tag, RET_CODE['pass']
    print(f'Failed Updating code for {project.name}', mark='fpull')
    return project.name, project.tag, RET_CODE['fail']


def install(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, int]:
    '''
    Install (update) from source code.

    Args:
        args:
            * env: installation context
            * project: project to delete

    Returns:
        project.name, project.tag, success code of action
    '''
    env, project = args
    if not (project.tag & ACTION_TAG['install']) or project.pull:
        tag = project.tag & (0xff - ACTION_TAG['install'])
        if env.verbose:
            print(f'Not trying to install {project.name}', mark='bug')
        return project.name, tag, RET_CODE['asis']
    install_call: typing.Callable = {
        0x10: install_make, 0x20: install_pip, 0x30: install_meson,
        0x40: install_go, 0x80: install_cmake
    }.get(project.tag&0xf0, lambda **_: True)
    success = install_call(code_path=os.path.join(env.clone_dir, project.name),
                           prefix=env.prefix, argv=project.inst_argv,
                           env=project.sh_env)
    if success:
        if env.verbose:
            print(f'Installed (update for) project {project.name}.',
                  mark='install')
        return project.name, project.tag & (0xff - ACTION_TAG['install']),\
            RET_CODE['pass']
        if env.verbose:
            print(f'FAILED Installing (update for) project {project.name}',
                  mark='finstall')
    return project.name, project.tag, RET_CODE['fail']


def success(
        args: typing.Tuple[InstallEnv, typing.Optional[GitProject]]
) -> typing.Tuple[str, int, int]:
    '''
    List successful projects

    Args:
        args:
            * env: installation context (ignored)
            * project: project to delete

    Returns:
        project.name, project.tag, ``RET_CODE``[``pass``]

    '''
    env, project = args
    if project is None:
        return 'None', 0x00, RET_CODE['asis']
    project.mark_update_time()
    print(f'{project.name} modified', mark='info')
    return project.name, project.tag, RET_CODE['pass']


def failure(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, int]:
    '''
    List failure points in projects

    Args:
        args:
            * env: installation context (ignored)
            * project: project to delete

    Returns:
        project.name, project.tag, ``RET_CODE``[``fail``]
    '''
    env, project = args
    if project.tag & ACTION_TAG['install']:
        print("Failed", project.name, mark='finstall')
        if env.verbose:
            if project.tag > 0x10:
                install_method = project.tag & 0xf0
                print(f'{FAIL_TAG[install_method]} for {project.name}',
                      mark='finstall')
    elif project.tag & ACTION_TAG['pull']:
        print("Failed", project.name, mark='fpull')
    elif project.tag & ACTION_TAG['delete']:
        print("Failed", project.name, mark='fdelete')
    return project.name, project.tag, RET_CODE['fail']
