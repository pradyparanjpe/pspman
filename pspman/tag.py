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


import typing


ACTION_TAG: typing.Dict[str, int] = {
    'info': 0x00,

    'make': 0x10,
    'pip': 0x20,
    'meson': 0x30,
    'go': 0x40,

    'pull': 0x01,
    'install': 0x02,
}
'''
Action: tag(int) codes
'''


TAG_ACTION: typing.Dict[int, str] = {
    0x00: 'info',

    0x10: 'make',
    0x20: 'pip',
    0x30: 'meson',
    0x40: 'go',

    0x01: 'pull',
    0x02: 'install',
}
'''
tag: Action (en)codes
'''


FAIL_TAG: typing.Dict[int, str] = {
    (0xf0 - 0x10): 'Make installation failed',
    (0xf0 - 0x20): 'Pip installation failed',
    (0xf0 - 0x30): 'Meson installation failed',
    (0xf0 - 0x40): 'Go installation failed',

    (0x0f - 0x01): 'Code-update failed',
    (0x0f - 0x02): 'Installation failed',
}
'''
tag(ing): Action-failure codes
'''
