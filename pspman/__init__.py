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
PSPMAN

'''


# Configure DEFAULT_PRINT
from psprint import DEFAULT_PRINT
DEFAULT_PRINT.switches['pad'] = True
DEFAULT_PRINT.print_kwargs['flush'] = True
DEFAULT_PRINT.switches['short'] = False
DEFAULT_PRINT.edit_style(mark='install', pref='INSTALL', pref_s='I',
                         pref_color='lg', pref_bgcol='k', text_color='g')

DEFAULT_PRINT.edit_style(mark='del', pref='DELETE', pref_s='D',
                         pref_color='ly', pref_bgcol='k', text_color='y')

DEFAULT_PRINT.edit_style(mark='pull', pref='CODE_UP', pref_s='C',
                         pref_color='lb', pref_bgcol='k', text_color='b')

DEFAULT_PRINT.edit_style(mark='clone', pref='CLONE', pref_s='a',
                         pref_color='lc', pref_bgcol='k', text_color='c')
print = DEFAULT_PRINT.psprint
'''
Customized psprint function

'''


__version__ = '21.2.23'
