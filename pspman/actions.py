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
parallel multiprocessed operations

All `actions` accept same set of args and return same type of object

    Args:
        * env: action context
        * project: project on which action is requested

    Returns:
        * project.name for indexing
        * project.tag feedback to update parent
        * success of action to inform parent

'''


import os
import typing
import shutil
from . import print
from .shell import git_comm
from .classes import InstallEnv, GitProject
from .tag import ACTION_TAG, FAIL_TAG, TAG_ACTION
from .installations import install_make, install_pip, install_meson, install_go


def delete(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, bool]:
    '''
    Delete this project

    Args:
        args:
            * env: installation context
            * project: project to delete

    Returns:
        project.name, project.tag, success of action

    '''
    env, project = args
    print_info = f'''
    Deleting {project.name}

    I can't guess which files were installed. So, leaving those scars behind...

    This project may be added again using:
    pspman -i {project.url}

    '''

    try:
        shutil.rmtree(os.path.join(env.clone_dir, project.name))
        print(print_info, mark='delete')
        return project.name, project.tag & (0xff - ACTION_TAG['delete']), True
    except OSError:
        print(f'Failed Deleting {project.name}', mark='fdelete')
        return project.name, project.tag, False


def clone(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, bool]:
    '''
    Get (clone) the remote project.url

        Args:
            args:
                * env: installation context
                * project: project to delete

    Returns:
        project.name, project.tag, success of action

    '''
    env, project = args
    if project.url is None:
        print(f'URL for {project.name} was not supplied', mark='err')
        return project.name, project.tag, False
    success = git_comm(clone_dir=os.path.join(env.clone_dir, project.name),
                       action='clone',
                       url=project.url, name=project.name)
    if success is None:
        # STDERR thrown
        print(f'Failed to clone source of {project.name}', mark='fclone')
        return (project.name, project.tag, False)
    project.type_install(env=env)
    if env.verbose:
        print(f'{project.name} cloned', mark='clone')
    tag = (project.tag | ACTION_TAG['install']) & (0xff - ACTION_TAG['pull'])
    return project.name, tag, True


def update(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, bool]:
    '''
    Update (pull) source code.
    Success means (Update successful or code is up-to-date)

    Args:
        args:
            * env: installation context
            * project: project to delete

    Returns:
        project.name, project.tag, success of action

    '''
    env, project = args
    g_pull = git_comm(clone_dir=os.path.join(env.clone_dir, project.name),
                      action='pull')
    if g_pull is not None:
        # STDERR from pull was blank
        tag = project.tag & (0xff - ACTION_TAG['pull'])
        if 'Already up to date' in g_pull:
            # Up to date
            if env.verbose:
                print(f'{project.name} is up to date.', mark='pull')
            return project.name, tag, True
        if 'Updating ' in g_pull:
            # STDOUT mentioned that the project was updated in some way
            tag |= ACTION_TAG['install']
            if env.verbose:
                print(f'{project.name} was updated.', mark='pull')
            return project.name, tag, True
    print(f'Failed Updating code for {project.name}', mark='fpull')
    return project.name, project.tag, False


def install(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, bool]:
    '''
    Install (update) from source code.

    Args:
        args:
            * env: installation context
            * project: project to delete

    Returns:
        project.name, project.tag, success of action
    '''
    env, project = args
    if not (project.tag & ACTION_TAG['install']):
        tag = project.tag & (0xff - ACTION_TAG['install'])
        if env.verbose:
            print(f'Not trying to install {project.name}', mark='bug')
        return project.name, tag, True
    install_call: typing.Callable = {
        1: install_make, 2: install_pip, 3: install_meson, 4: install_go,
    }.get(int(project.tag//0x10), lambda **_: True)
    success = install_call(
        code_path=os.path.join(env.clone_dir, project.name),
        prefix=env.prefix, argv=project.inst_argv, env=project.sh_env
    )
    if success:
        if env.verbose:
            print(f'Installed (update for) project {project.name}.',
                  mark='install')
        return project.name, project.tag & (0xff - ACTION_TAG['install']), True
        if env.verbose:
            print(f'FAILED Installing (update for) project {project.name}',
                  mark='finstall')
    return project.name, project.tag, False


def success(
        args: typing.Tuple[InstallEnv, typing.Optional[GitProject]]
) -> typing.Tuple[str, int, bool]:
    '''
    List successful projects

    Args:
        args:
            * env: installation context (ignored)
            * project: project to delete

    '''
    env, project = args
    if project is None:
        return 'None', 0x00, True
    project.mark_update_time()
    print(f'{project.name} processed', mark='info')
    return project.name, project.tag, True


def failure(
        args: typing.Tuple[InstallEnv, GitProject]
) -> typing.Tuple[str, int, bool]:
    '''
    List failure points in projects

    Args:
        args:
            * env: installation context (ignored)
            * project: project to delete

    '''
    env, project = args
    if project.tag & ACTION_TAG['install']:
        print("Failed", project.name, mark='finstall')
        if env.verbose:
            if project.tag > 0x10:
                install_method = project.tag & 0xF0
                print(f'{FAIL_TAG[install_method]} for {project.name}',
                      mark='finstall')
    elif project.tag & ACTION_TAG['pull']:
        print("Failed", project.name, mark='fpull')
    elif project.tag & ACTION_TAG['delete']:
        print("Failed", project.name, mark='fdelete')
    return project.name, project.tag, False
