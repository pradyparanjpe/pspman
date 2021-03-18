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
shell functions

'''


import os
import typing
import subprocess
from .errors import CommandError
from . import print


def process_comm(*cmd: str, p_name: str = 'processing', timeout: int = None,
                 fail_handle: str = 'fail', **kwargs) -> typing.Optional[str]:
    '''
    Generic process definition and communication.
    Raw actions, outputs, errors are displayed
    when the parent program is called with
    the environment variable ``DEBUG`` = ``True``

    Args:
        *cmd: list(cmd) is passed to subprocess.Popen as first argument
        p_name: notified as 'Error {p_name}: {stderr}
        timeout: communicatoin timeout. If -1, 'communicate' isn't called
        fail: {fail,nag,report,ignore}
            * fail: raises CommandError
            * nag: Returns None, prints stderr
            * report: returns None, but hides stderr
            * ignore: returns stdout, despite error (default behaviour)
        **kwargs: all are passed to ``subprocess.Popen``

    Returns:
        stdout from command's communication
        ``None`` if stderr with 'fail == False'

    Raises:
        CommandError

    '''
    cmd_l = list(cmd)
    if timeout is not None and timeout < 0:
        process = subprocess.Popen(cmd_l, **kwargs)  # DONT: *cmd_l here
        return None
    process = subprocess.Popen(cmd_l, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, **kwargs)
    stdout, stderr = process.communicate(timeout=timeout)
    if os.environ.get('DEBUG', False):
        print(cmd_l, mark='act')
        print(stdout, mark='bug')
        print(stderr, mark='err')
        print("return:", process.returncode, mark='err')
    if process.returncode != 0:
        if fail_handle == 'fail':
            raise CommandError(cmd_l, stderr)
        if fail_handle in ('report', 'nag'):
            if fail_handle == 'nag':
                print(stderr, mark=4)
            return None
    return stdout


def git_comm(
        clone_dir: str,
        motive: typing.Union[str, typing.Tuple[str, str]] = None,
        gitkwargs: typing.Dict[str, typing.Optional[str]] = None,
        prockwargs: typing.Dict[str, str] = None) -> typing.Optional[str]:
    '''
    Perform a git action

    Args:
        clone_dir: directory in which, project is (to be) cloned
        motive: git action to perform
            * list: list git projects (default)
            * pull: pull and update
            * (url, name): clone a new project identified by (url, name)

                * url: remote url to clone
                * name: name (path) of project

        gitkwargs: parsed from to --key[=val] and passed to git command
        prockwargs: passed to ``process_comm``

    Returns:
        Output from process_comm

    '''
    # Default $0 command
    cmd: typing.List[str] = ['git']

    # process kwargs
    if prockwargs is None:
        prockwargs = {}

    if gitkwargs is None:
        gitkwargs = {}

    if isinstance(motive, str):
        if motive == 'pull':
            cmd.extend(('-C', clone_dir, 'pull', '--recurse-submodules'))
        else:
            cmd.extend(("-C", clone_dir, 'remote', "-v"))
    else:
        if not isinstance(motive, (tuple, list)) or len(motive) != 2:
            return None
        url, name = motive
        if not(isinstance(url, str) and isinstance(name, str)):
            return None
        cmd.extend(('-C', os.path.split(clone_dir)[0], 'clone', url, name))

    # Parse gitkwargs into arguments
    for key, val in gitkwargs.items():
        key_flag = "-" + str(key) if len(str(key)) < 2 else "--" + str(key)
        cmd.append(key_flag)
        if val is not None:
            cmd.append(str(val))

    return process_comm(*cmd, p_name=f'git {motive}', timeout=None,
                        fail_handle='report', **prockwargs)
