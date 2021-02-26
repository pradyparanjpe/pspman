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
print = DEFAULT_PRINT.psprint
'''
Customized psprint function

'''


from .command_line import call
__all__ = ['call']
__version__ = '21.2.23'
