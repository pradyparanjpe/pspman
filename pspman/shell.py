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


import typing
import subprocess
from .psprint import print
from .errors import CommandError


def process_comm(*cmd: str,
                 p_name: str = 'processing',
                 timeout: int = None,
                 fail_handle: str = 'fail',
                 **kwargs) -> typing.Optional[str]:
    '''
    Generic process definition and communication.

    Args:
        *cmd: list(cmd) is passed to subprocess.Popen as first argument
        p_name: notified as 'Error {p_name}: {stderr}
        timeout: communicatoin timeout. If -1, 'communicate' isn't called
        fail: {fail,nag,report,ignore}

            fail: raises CommandError
            nag: Returns None, prints stderr
            ignore: returns stdout, despite error

        **kwargs: passed on to subprocess.Popen
            * bug: bool: ?print debugging output [action, stdout, stderr]


    Returns:
        stdout from command's communication
        ``None`` if stderr with 'fail == False'

    Raises:
        CommandError
    '''
    cmd_l = list(cmd)
    bug: bool = False
    if 'bug' in kwargs:
        bug = kwargs.get('bug', False)
        del kwargs['bug']
    if timeout is not None and timeout < 0:
        process = subprocess.Popen(cmd_l, **kwargs)  # DONT: *cmd_l here
        return None
    process = subprocess.Popen(
        cmd_l,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        **kwargs
    )
    stdout, stderr = process.communicate(timeout=timeout)
    if bug:
        print(cmd_l, mark='act')
        print(stdout, mark='bug')
        print(stderr, mark='err')
    if stderr:
        if fail_handle == 'fail':
            raise CommandError(cmd_l, stderr)
        if fail_handle in ('report', 'nag'):
            if fail_handle == 'nag':
                print(f"{stderr}", mark=4)
            return None
    return stdout


def git_comm(clone_dir: str,
             action: str = None,
             url: str = None,
             name: str = None,
             **kwargs) -> typing.Optional[str]:
    '''
    Perform a git action

    Args:
        clone_dir: directory in which, project is (to be) cloned
        action: git action to perform
            * list: list git projects (default)
            * pull: pull and update
            * clone: clone a new project (requires ``name``, ``url``)

        url: remote url to clone (required for ``action`` == 'clone')
        name: name (path) of project (required for ``action`` == 'clone')

    Returns:
        Output from process_comm

    '''
    cmd: typing.List[str] = ['git', '-C', clone_dir]
    fail_handle = 'report'
    if action == 'pull':
        cmd.extend(('pull', '--recurse-submodules'))
        fail_handle = 'ignore'
    if action == 'clone':
        if url is None or name is None:
            # required
            return None
        cmd.extend(('clone', url, name))
    elif action in (None, 'list'):
        cmd.extend(('remote', '-v'))
    return process_comm(*cmd, p_name=f'git {action}',
                        fail_handle=fail_handle, **kwargs)
