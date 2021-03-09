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
from . import CONFIG
from .psprint import print
from .shell import git_comm
from .classes import GitProject, PSPManDB
from .tag import ACTION_TAG, FAIL_TAG, TAG_ACTION
from .installations import (install_make, install_pip,
                            install_meson, install_go)


def delete(project: GitProject) -> typing.Tuple[str, str, int, bool]:
    '''
    Delete this project

    Args:
        project: project to delete

    Returns:
        project.name, print_info, success of action

    '''
    print_info = f'''
    Deleting {project.name}

    I can't guess which files were installed. So, leaving those scars behind...

    This project may be added again using:
    pspman -i {project.url}

    '''

    try:
        shutil.rmtree(os.path.join(CONFIG.clone_dir, project.name))
        return (project.name, print_info,
                project.tag & (0xff - ACTION_TAG['delete']), True)
    except OSError:
        print_info = "FAILED!!!\n" + print_info
        return project.name, print_info, project.tag, False


def clone(project: GitProject) -> typing.Tuple[str, str, int, bool]:
    '''
    Get (clone) the remote project.url

    Args:
        project: project to clone

    Returns:
        project.name, print_info, success of action

    '''
    print_info = f'Cloned source of {project.name}'
    if project.url is None:
        return (project.name, 'Unknown Clone URL', project.tag, False)
    success = git_comm(clone_dir=os.path.join(CONFIG.clone_dir, project.name),
                       action='clone',
                       url=project.url, name=project.name)
    if success is None:
        print_info = f'FAILED Cloning source of {project.name}'
        return (project.name, print_info, project.tag, False)
    project.type_install()
    return (project.name, print_info,
            (project.tag | ACTION_TAG['install']) &
            (0xff - ACTION_TAG['pull']), True)


def update(project: GitProject) -> typing.Tuple[str, str, int, bool]:
    '''
    Update (pull) source code.
    Success means (Update successful or code is up-to-date)

    Args:
        project: project to update

    Returns:
        project.name, print_info, success of action

    '''
    print_info = f'{project.name} is up to date.'
    g_pull = git_comm(clone_dir=os.path.join(CONFIG.clone_dir, project.name),
                      action='pull')
    tag = project.tag & (0xff - ACTION_TAG['pull'])
    if g_pull and 'Already up to date' not in g_pull:
        print_info = f'Updated code for {project.name}'
        if 'Updating ' not in g_pull:
            print_info = f'FAILED Updating code for {project.name}'
            return project.name, print_info, tag, False
        tag |=  ACTION_TAG['install']
    return project.name, print_info, tag, True


def install(project: GitProject) -> typing.Tuple[str, str, int, bool]:
    '''
    Install (update) from source code.

    Args:
        project: GitProject: project to install

    Returns:
        project.name, print_info, success of action

    '''
    print_info = f'Not trying to install {project.name}'
    install_call: typing.Callable = {
        1: install_make, 2: install_pip, 3: install_meson, 4: install_go,
    }.get(int(project.tag//0x10), lambda **_: True)
    if not project.tag & ACTION_TAG['install']:
        return project.name, print_info, project.tag, True
    success = install_call(
        code_path=os.path.join(CONFIG.clone_dir, project.name),
        prefix=CONFIG.prefix
    )
    if success:
        print_info = f'Installed project {project.name}'
        return (project.name, print_info,
                project.tag & (0xff - ACTION_TAG['install']), True)
    print_info = f'FAILED Installing project {project.name}'
    return (project.name, print_info, project.tag , False)


def success(project: GitProject) -> typing.Tuple[str, str, int, bool]:
    '''
    List successful projects

    Args:
        project: GitProject: project that completed successfully

    '''
    project.mark_update_time()
    # push back to parent
    if project.tag & 0x04:
        print(project.name, mark='install')
    elif project.tag & 0x02:
        print(project.name, mark='pull')
    elif project.tag & 0x01:
        print(project.name, mark='delete')
    return project.name, '', project.tag, True


def failure(project: GitProject) -> typing.Tuple[str, str, int, bool]:
    '''
    List failure points in projects

    Args:
        project: GitProject: project that failed

    '''
    print(f'{FAIL_TAG[project.tag & 0x0F]} for {project.name}',
          mark='err')
    return project.name, '', project.tag, True
