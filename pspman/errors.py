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


class TagError(Exception):
    '''
    Error in tagging a git for type of modification (pull, install, etc)

    Args:
        old_tag: existing tag
        operate: operation intended

    '''

    def __init__(self, old_tag: int, operate: str) -> None:
        super().__init__(f'''
        Tag '{old_tag}' can't be operated by '{operate}'
        ''')
