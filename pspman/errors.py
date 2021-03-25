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
Exceptions, Warnings, Errors
'''


import os
import typing


class PSPManError(Exception):
    '''
    base error for papman
    '''


class TagError(PSPManError):
    '''
    Error in tagging a git for type of modification (pull, install, etc)

    Args:
        old_tag: existing tag
        operate: operation intended

    '''

    def __init__(self, old_tag: int, operate: str) -> None:
        super(PSPManError, self).__init__(f'''
        Tag '{old_tag}' can't be operated by '{operate}'
        ''')


class ClosedQueueError(PSPManError):
    '''
    Operation can't be performed, since the queue has been closed

    Args:
        queue: PSPQueue: the queue that threw the error

    '''
    def __init__(self, queue):
        super(PSPManError, self).__init__('''
        {type(queue)} Queue is closed
        ''')


class PathNameError(PSPManError):
    '''
    Path/URL (and hence or otherwise, name) can't be determined
    '''
    def __init__(self):
        super(PSPManError, self).__init__(f'''
        Path and/name not found/inferred
        ''')


class GitURLError(PathNameError):
    '''
    Git URL (and hence or otherwise, name) can't be determined
    '''
    def __init__(self):
        super(PSPManError, self).__init__(f'''
        GIT URL and/name not found/inferred
        ''')


class CommandError(PSPManError):
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

class InstructError(PSPManError):
    '''
    Base class for instruction files error
    '''

class InstructFmtError(InstructError):
    '''
    Error parsing installation instructions file

    Args:
        instruct_file: name of file with fault
    '''
    def __init__(self, instruct_file: typing.Union[str, os.PathLike],
                 *args) -> None:
        super().__init__(self, f'{instruct_file} is incorrectly formatted')

class MissingInstructError(InstructError):
    '''
    Error in installation instructions file: necessary instruction missing

    Args:
        instruct_file: name of file with fault
        missing: name of argument missing
    '''
    def __init__(self, missing: str) -> None:
        super().__init__(self, f'missing instruction: {missing}')

class InstructTypeError(TypeError, InstructError):
    '''
    Wrong type of instruction
    '''
    def __init__(self, key: str, found_type: type, want_type: str):
        super().__init__(
            self, f'{key}: is of type: {found_type}; expected: {want_type}'
        )
