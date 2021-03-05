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
parallel threading/multithreading operations

'''


import os
import typing
import shutil
from . import print
from .shell import git_comm
from .classes import InstallEnv, GitProject, PSPManDB
from .tag import ACTION_TAG, FAIL_TAG, TAG_ACTION
from .installations import (install_make, install_pip,
                            install_meson, install_go)


def delete(args) -> typing.Tuple[str, str, bool]:
    '''
    Delete this project

    Args:
        args:
            project: GitProject: project to delete
            env: InstallEnv: current environment background

    Returns:
        project.name, print_info, success of action

    '''
    project: GitProject
    env: InstallEnv
    project, env, *_ = args
    print_info = f'''
    Deleting {project.name}

    I can't guess which files were installed. So, leaving those scars behind...

    This project may be added again using:
    pspman -i {project.url}

    '''

    try:
        shutil.rmtree(os.path.join(env.clone_dir, project.name))
        return project.name, print_info, True
    except OSError:
        print_info = "FAILED!!!\n" + print_info
        return project.name, print_info, False


def clone(args) -> typing.Tuple[str, str, bool]:
    '''
    Get (clone) the remote project.url

    Args:
        args:
            project: GitProject: project to clone
            env: InstallEnv: current environment background

    Returns:
        project.name, print_info, success of action

    '''
    project: GitProject
    env: InstallEnv
    project, env, *_ = args
    print_info = f'Cloned source of {project.name}'
    if project.url is None:
        return project.name, 'Unknown Clone URL', False
    success = git_comm('clone', os.path.join(env.clone_dir, project.name),
                       project.url, project.name)
    if success is None:
        print_info = f'FAILED Cloning source of {project.name}'
        return project.name, print_info, False
    project.type_install(env=env)
    return project.name, print_info, True


def update(args) -> typing.Tuple[str, str, bool]:
    '''
    Update (pull) source code.
    Success means (Update successful or code is up-to-date)

    Args:
        args:
            project: GitProject: project to update
            env: InstallEnv: current environment background

    Returns:
        project.name, print_info, success of action

    '''
    project: GitProject
    env: InstallEnv
    project, env, *_ = args
    print_info = f'{project.name} is up to date.'
    g_pull = git_comm('pull', os.path.join(env.clone_dir, project.name))
    if g_pull and 'Already up to date' not in g_pull:
        print_info = f'Updated code for {project.name}'
        if 'Updating ' not in g_pull:
            print_info = f'FAILED Updating code for {project.name}'
            return project.name, print_info, False
    return project.name, print_info, True


def install(args) -> typing.Tuple[str, str, bool]:
    '''
    Install (update) from source code.

    Args:
        args:
            project: GitProject: project to install
            env: InstallEnv: current environment background

    Returns:
        project.name, print_info, success of action

    '''
    project: GitProject
    env: InstallEnv
    project, env, *_ = args
    print_info = f'Not trying to install {project.name}'
    install_call: typing.Callable = {
        1: install_make, 2: install_pip, 3: install_meson, 4: install_go,
    }.get(int(project.tag//0x10), lambda **_: True)
    if not project.tag & ACTION_TAG['install']:
        return project.name, print_info, True
    success = install_call(
        code_path=os.path.join(env.clone_dir, project.name),
        prefix=env.prefix
    )
    if success:
        print_info = f'Installed project {project.name}'
        return project.name, print_info, True
    print_info = f'FAILED Installing project {project.name}'
    return project.name, print_info, False


def success(args) -> typing.Tuple[str, str, bool]:
    '''
    List successful projects

    Args:
        args:
            project: GitProject: project that completed successfully
            env: ignored

    '''
    project: GitProject
    project, *_ = args
    project.mark_update_time()
    performed = TAG_ACTION[project.tag & 0x01]
    # push back to parent
    print(project.name, mark=performed)
    return project.name, '', True


def failure(args) -> typing.Tuple[str, str, bool]:
    '''
    List failure points in projects

    Args:
        args:
            project: GitProject: project that failed
            env: ignored

    '''
    project: GitProject
    project, *_ = args
    print(f'{FAIL_TAG[project.tag & 0x0F]} for {project.name}',
          mark='err')
    return project.name, '', True
