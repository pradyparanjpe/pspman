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
PSPMAN: **PS**\ eudo **P**\ ackage **Man**\ ager

'''


# Globally defined environment configuration
import os
from psprint import init_print
from .classes import InstallEnv


print = init_print(os.path.join(os.path.dirname(__file__),
                                ".psprintrc.yml")).psprint
'''
Customized psprint function

'''


# set configurations
ENV = InstallEnv()
'''
Standard installation context
'''


__version__ = '1!0.1.0'
