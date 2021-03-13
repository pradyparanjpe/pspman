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


def git_comm(clone_dir: str, action: str = None, url: str = None,
             name: str = None, **kwargs) -> typing.Optional[str]:
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
        **kwargs:
            * passed to ``process_comm``

    Returns:
        Output from process_comm

    '''
    if action == 'clone' and any(req is None for req in (url, name)):
        # required with action == 'clone'
        return None
    cmd: typing.List[str] = ['git', '-C']
    git_args: typing.Dict[str, typing.Tuple[str, ...]] = {
        'clone': (os.path.split(clone_dir)[0],  # type: ignore
                  'clone', url, name),
        'list': (clone_dir, 'remote', '-v'),
        'pull': (clone_dir, 'pull', '--recurse-submodules'),
    }
    cmd.extend(git_args[action or 'list'])
    return process_comm(*cmd, p_name=f'git {action}',
                        fail_handle='report', **kwargs)
