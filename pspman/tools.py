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
Miscellaneous tools

'''


import time


def timeout(wait: int = 10) -> None:
    '''
    Print a count-down time that waits for the process to get killed

    Args:
        wait: wait for seconds

    '''
    for time_out in range(wait):
        time.sleep(1)
        print(f"{wait - time_out:2.0f} seconds...", end='', flush=True)
        print("\b" * 13, end='', flush=True)
    print(f"{wait:2.0f} seconds...", flush=True)
