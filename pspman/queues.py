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
Command Queues

'''


import typing


class PSPQueue:
    '''
    Base FIFO Queue object to push and retrieve tasks
    '''
    def __init__(self):
        self.queue: typing.List[object] = []

    def next(self) -> object:
        '''
        Pop out 0th object reference in queue

        Raises:
            IndexError: No more objects in queue
        '''
        return self.queue.pop(0)

    def add(self, obj_ref) -> None:
        '''
        Add obj_ref to queue at the end
        '''
        self.queue.append(obj_ref)

    def __len__(self) -> int:
        '''
        length of ojects in the queue
        '''
        return len(self.queue)

    def __iter__(self) -> typing.Iterable:
        '''
        An iterable object
        '''
        return self.queue.__iter__()


class PullQueue(PSPQueue):
    '''
    Queue of source codes to pull
    '''


class InstallQueue(PSPQueue):
    '''
    Queue of projects to install
    '''


class ErrorQueue(PSPQueue):
    '''
    Queue of Errors to Report
    '''
