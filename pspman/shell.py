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
from . import print


class CommandError(Exception):
    '''
    Base class for subprocess failure

    Args:
        cmd: command passed to shell for execution
        err: stderr received from shell after failure

    '''
    def __init__(self, cmd: list, err: str = None) -> None:
        super().__init__(self, f'''
        Command Passed for execution:
        {cmd}

        STDERR from command:
        {err}
        ''')


def process_comm(*cmd: str, p_name: str = 'processing', timeout: int = None,
                 fail_handle: str = 'fail', **kwargs) -> typing.Optional[str]:
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
    process = subprocess.Popen(
        cmd_l,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        **kwargs
    )
    stdout, stderr = process.communicate(timeout=timeout)
    print(stdout, mark='bug')
    if stderr:
        if fail_handle == 'fail':
            raise CommandError(cmd_l, stderr)
        if fail_handle in ('report', 'nag'):
            if fail_handle == 'nag':
                print(f"{stderr}", mark=4)
            return None
    return stdout
