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
Tags

'''


from .errors import TagError


class ActionTag():
    '''
    Coded information about update method.
    For Bytecode B, B < 8: F - B = Failure Code

    Attributes:
        Tag:

            * 0x00: Do nothing
            * 0xFF: Failed at everything

            * 0x01: List
            * 0x02: Pull
            * 0x04: Try install

            * 0x0B: Install Failed
            * 0x0D: Pull Failed
            * 0x0E: List Failed

            * 0x10: Make
            * 0x20: Pip
            * 0x30: Meson/Ninja
            * 0x40: Go

            * 0xB0: Go failed
            * 0xC0: Meson/Ninja failed
            * 0xD0: Pip failed
            * 0xE0: Make Failed

    '''

    def __init__(self, x: int = 0) -> None:
        self.tag = x

    def show_list(self) -> None:
        '''
        flag show in list
        '''
        self.tag |= 0x01

    def pull(self) -> None:
        '''
        flag pull = True
        '''
        self.tag |= 0x02

    def try_install(self) -> None:
        '''
        flag install try
        '''
        self.tag |= 0x04

    def make(self) -> None:
        '''
        flag install for make method

        Raises:
            TagError: already tagged

        '''
        if (0x0 < self.tag//0x10 < 0x5):
            if not self.tag & 0x10:
                # already tagged
                raise TagError(self.tag, 'make')
        else:
            self.tag |= 0x10

    def pip(self) -> None:
        '''
        flag install for pip

        Raises:
            TagError: already tagged

        '''
        if (0x0 < self.tag//0x10 < 0x5):
            if not self.tag & 0x20:
                # already tagged
                raise TagError(self.tag, 'pip')
        else:
            self.tag |= 0x20

    def meson(self) -> None:
        '''
        flag install for meson

        Raises:
            TagError: already tagged

        '''
        if (0x0 < self.tag//0x10 < 0x5):
            if not self.tag & 0x30:
                # already tagged
                raise TagError(self.tag, 'meson')
        else:
            self.tag |= 0x30

    def goin(self) -> None:
        '''
        flag install for go

        Raises:
            TagError: already tagged

        '''
        if (0x0 < self.tag//0x10 < 0x5):
            if not self.tag & 0x40:
                # already tagged
                raise TagError(self.tag, 'go')
        else:
            self.tag |= 0x40

    def err(self) -> None:
        '''
        Invert flags due to error

        '''
        self.tag = 0xff - self.tag
