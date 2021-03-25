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
Tags

'''


import typing


ACTION_TAG: typing.Dict[str, int] = {
    'info': 0x00,  # nothing
    'delete': 0x01,
    'pull': 0x02,
    'install': 0x04,
}
'''
Action: tag(int) codes
'''


TAG_ACTION: typing.Dict[int, str] = {
    0x00: 'info',  # nothing
    0x01: 'delete',
    0x02: 'pull',
    0x04: 'install',
}
'''
tag: Action (en)codes
'''


FAIL_TAG: typing.Dict[int, str] = {
    0x01: 'Code-delete failed',
    0x02: 'Code-update failed',
    0x04: 'Installation failed',
    0x00: 'Processed everything',
}
'''
tag(ing): Action-failure codes
'''


RET_CODE: typing.Dict[str, int] = {
    'pass': 1,
    'fail': 0,
    'asis': -1, # not modified
}
'''
Codes returned by functions in ``action`` module
'''
