#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This file is part of pspman. #
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


import typing
import shutil
from pathlib import Path
from . import print, CONFIG
from .shell import git_clean, git_pull, git_clone
from .classes import InstallEnv, GitProject
from .tag import ACTION_TAG, FAIL_TAG, TAG_ACTION, RET_CODE
from .installations import INST_METHODS, run_install


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
    # Attempt uninstallation
    code_path = Path(env.clone_dir).joinpath(project.name)
    i_type = None
    for method_name, method in INST_METHODS.items():
        if (any(code_path.joinpath(id_file).exists()
                for id_file in method.instruct.indicate) and not
            any(code_path.joinpath(xd_file).exists()
                for xd_file in method.instruct.exdicate)):
            i_type = method_name
            break
    if i_type is not None:
        # Known uninstallation method
        if env.verbose:
            print( f'''
            Trying standard uninstall calls with {i_type}.
            This may not always be clean; some scars may stay back.
            ''', mark='delete')
        success = run_install(i_type='u_' + i_type, code_path=code_path,
                              prefix=env.prefix, argv=project.inst_argv,
                              env=project.sh_env)
        if not success:
            if env.verbose:
                print(f'FAILED Uninstalling project {project.name}',
                      mark='fdelete')
                print(f'Proceeding to delete the source code anyway..',
                      mark='info')
    else:
        if env.verbose:
            print(f'PSPMan was initialized only with {CONFIG.opt_in}')

    # Erase source code
    if env.verbose:
        print('Erasing source code', mark='delete')
    try:
        shutil.rmtree(Path(env.clone_dir).joinpath(project.name))
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
    ret = git_clone(clone_dir=Path(env.clone_dir).joinpath(project.name),
                    url=project.url, name=project.name, gitkwargs=gitkwargs)
    if ret is None:
        # STDERR thrown
        print(f'Failed to clone source of {project.name}', mark='fclone')
        return (project.name, project.tag, RET_CODE['fail'])
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
    code_path = Path(env.clone_dir).joinpath(project.name)
    g_pull = git_pull(clone_dir=code_path)
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
    code_path = Path(env.clone_dir).joinpath(project.name)
    i_type = None
    for method_name, method in INST_METHODS.items():
        if (any(code_path.joinpath(id_file).exists()
                for id_file in method.instruct.indicate) and not
            any(code_path.joinpath(xd_file).exists()
                for xd_file in method.instruct.exdicate)):
            i_type = method_name
            break
    if i_type is not None:
        success = run_install(i_type=i_type, code_path=code_path,
                              prefix=env.prefix, argv=project.inst_argv,
                              env=project.sh_env)
        if success:
            if env.verbose:
                print(f'Installed (update for) project {project.name}.',
                      mark='install')
            git_clean(code_path)
            return project.name, project.tag & (0xff - ACTION_TAG['install']),\
                RET_CODE['pass']
    if env.verbose:
        print(f'FAILED Installing (update for) project {project.name}',
              mark='finstall')
        if TAG_ACTION[project.tag&0xf0] not in CONFIG.opt_in:
            print(f'PSPMan was initialized only with {CONFIG.opt_in}')
    git_clean(code_path)
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
