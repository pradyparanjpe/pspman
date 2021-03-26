#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This file is part of pspman.
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
from pathlib import Path
import re
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
        print("returncode:", process.returncode, mark='err')
    if process.returncode != 0:
        if fail_handle == 'fail':
            raise CommandError(cmd_l, stderr)
        if fail_handle in ('report', 'nag'):
            if fail_handle == 'nag':
                print(stderr, mark=4)
            return None
    return stdout or 'success'


def git_comm(cmd: typing.List[str], g_name: str = 'process', gitkwargs:
             typing.Dict[str, typing.Optional[str]] = None, prockwargs:
             typing.Dict[str, typing.Any] = None) -> typing.Optional[str]:
    '''
    Process git-specific and subprocess-specific kwargs and run git cmd

    Args:
        cmd: command list to run
        gitkwargs: parsed from to --key[=val] and passed to git command
        prockwargs: passed to ``process_comm``

    Returns:
        Output from process_comm

    '''

    # process kwargs
    prockwargs = prockwargs or {}
    gitkwargs = gitkwargs or {}

    # Parse gitkwargs into arguments
    for key, val in gitkwargs.items():
        key_flag = "-" + str(key) if len(str(key)) < 2 else "--" + str(key)
        cmd.append(key_flag)
        if val is not None:
            cmd.append(str(val))
    return process_comm(*cmd, p_name=f'git {g_name}', timeout=None,
                        fail_handle='report', **prockwargs)


def git_clean(clone_dir: Path, gitkwargs:
              typing.Dict[str, typing.Optional[str]] = None,
              prockwargs: typing.Dict[str, typing.Any]
              = None) -> typing.Optional[str]:
    '''
    Reset and clean git worktree

    Args:
        clone_dir: directory in which, project is (to be) cloned

    Returns:
        Output from process_comm

    '''
    checkout = ['git', '-C', str(clone_dir), 'checkout', 'HEAD', '--', ':/']
    clean = ['git', '-C', str(clone_dir), 'clean', '-f', '--', ':/']
    if not bool(git_comm(checkout, g_name='checkout', gitkwargs=gitkwargs,
                         prockwargs=prockwargs)):
        return None
    return git_comm(clean, g_name='clean', gitkwargs=gitkwargs,
                    prockwargs=prockwargs)


def git_list(clone_dir: Path, gitkwargs: typing.Dict[str, typing.Optional[str]]
             = None, prockwargs: typing.Dict[str, typing.Any]
             = None) -> typing.Optional[str]:
    '''
    Generate remote url of git

    Args:
        clone_dir: directory in which, project is (to be) cloned
        gitkwargs: parsed from to --key[=val] and passed to git command
        prockwargs: passed to ``process_comm``

    Returns:
        Output from process_comm

    '''
    # Default $0 command
    cmd: typing.List[str] = ['git', "-C", str(clone_dir), 'remote', "-v"]
    remote = git_comm(cmd, g_name='list',
                    gitkwargs=gitkwargs, prockwargs=prockwargs)
    if remote is None:
        # failed
        return None
    fetch: typing.List[str] = re.findall(r"^.*fetch.*", remote)
    url = fetch[0].split(' ')[-2].split("\t")[-1].rstrip('/')
    return url

def git_pull(clone_dir: Path, gitkwargs: typing.Dict[str, typing.Optional[str]]
             = None, prockwargs: typing.Dict[str, typing.Any]
             = None) -> typing.Optional[str]:
    '''
    Perform a git action

    Args:
        clone_dir: directory in which, project is (to be) cloned
        gitkwargs: parsed from to --key[=val] and passed to git command
        prockwargs: passed to ``process_comm``

    Returns:
        Output from process_comm

    '''
    # Default $0 command
    cmd: typing.List[str] = ['git', '-C', str(clone_dir),
                             'pull', '--recurse-submodules']
    return git_comm(cmd, g_name='pull',
                    gitkwargs=gitkwargs, prockwargs=prockwargs)

def git_clone(clone_dir: Path, url: str, name: str, gitkwargs:
              typing.Dict[str, typing.Optional[str]] = None, prockwargs:
              typing.Dict[str, typing.Any] = None) -> typing.Optional[str]:
    '''
    Perform a git action

    Args:
        clone_dir: directory in which, project is (to be) cloned
        url: remote url to clone
        name: name (path) of project
        gitkwargs: parsed from to --key[=val] and passed to git command
        prockwargs: passed to ``process_comm``

    Returns:
        Output from process_comm

    '''
    # Default $0 command
    cmd: typing.List[str] = ['git', '-C', str(clone_dir.parent),
                             'clone', url, name]
    return git_comm(cmd, g_name='clone',
                    gitkwargs=gitkwargs, prockwargs=prockwargs)
