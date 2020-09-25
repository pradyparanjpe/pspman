#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This le is part of pspman.
#
# pspman is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pspman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pspman.  If not, see <https://www.gnu.org/licenses/>.
#
'''
input/outputs
'''


from os import getcwd, environ
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from colorama import Fore, Style


def print_info(out_msg: str = '', p_type: int = 0, **kwargs) -> None:
    '''
    out_msg: Printed with an prefix of p_type
    p_type: interpreted type to prefix out_msg
    0: continuation
    1: information
    2: action
    3: warning
    4: error
    5: list
    6: debug
    *: <empty>
    **kwargs: passed to print function
    '''
    emit_l = [
        Style.RESET_ALL + '          ' + Style.RESET_ALL,
        Fore.GREEN +      ' [INFORM] ' + Style.RESET_ALL,
        Fore.YELLOW +     ' [ACTION] ' + Style.RESET_ALL,
        Fore.MAGENTA +    '[WARNING] ' + Style.RESET_ALL,
        Fore.RED +        '  [ERROR] ' + Style.RESET_ALL,
        Fore.BLUE +       '   [LIST] ' + Style.RESET_ALL,
        Fore.CYAN +       '  [DEBUG] ' + Style.RESET_ALL,
    ]
    if not (0 <= p_type <= 6):
        p_type = 0
    print(emit_l[p_type] + str(out_msg), **kwargs, flush=True)


def cli() -> Namespace:
    '''
    Parse command line arguments
    '''
    description = '''
    NOTICE: This is only intended for \"user\" installs.
    CAUTION: DO NOT RUN THIS SCRIPT AS ROOT.
    CAUTION: If you still insist, I won't care.
    '''
    homedir = environ["HOME"]
    parser = ArgumentParser(description=description,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--force-root', action='store_true',
                        help='force working with root permissions [DANGEROUS]')
    parser.add_argument('-o', '--only-pull', action='store_true',
                        help='only pull, do not try to install')
    parser.add_argument('-c', '--clone-dir', type=str, nargs="?",
                        default=f'{homedir}/programs',
                        help='path for all git clones')
    parser.add_argument('-p', '--prefix', type=str, nargs="?",
                        default=f'{homedir}',
                        help='path for installation')
    parser.add_argument('-i', '--pkg-install', metavar='URL', type=str,
                        nargs="*", help='URL to clone new project')
    parser.add_argument('-d', '--pkg-delete', metavar='PROJ', type=str,
                        nargs="*", help='PROJ to clone new project')
    args = parser.parse_args()
    return args
