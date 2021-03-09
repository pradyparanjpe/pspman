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
Define variables from command line and defaults

'''


import os
import typing
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import argcomplete
from .psprint import print
from .shell import process_comm
from .tools import timeout


class DefConfig():
    '''
    Configuration variables

    Attributes:

    Args:
        **kwargs: set attributes

    '''
    def __init__(self):
        self.call_function: typing.Optional[str] = None
        self._clone_dir: typing.Optional[str] = None
        self._prefix: typing.Optional[str] = None
        self.risk: bool = False
        self.pull: bool = False
        self.stale: bool = False
        self.verbose: bool = False
        self.proj_install: typing.List[str] = []
        self.proj_delete: typing.List[str] = []

    @property
    def clone_dir(self) -> str:
        if self._clone_dir is None:
            self._clone_dir = os.path.join(os.environ['HOME'], ".pspman")
        return os.path.join(self._clone_dir, 'src')

    @clone_dir.setter
    def clone_dir(self, value):
        self._clone_dir = value

    @clone_dir.deleter
    def clone_dir(self):
        self._clone_dir = os.path.join(os.environ['HOME'], ".pspman")

    @property
    def prefix(self) -> str:
        if self._prefix is None:
            self._prefix = os.path.split(self.clone_dir)[0]
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self._prefix = value

    @prefix.deleter
    def prefix(self):
        self._prefix = self.clone_dir

    def __repr__(self) -> str:
        return  f'''
        Clone Directory: {self.clone_dir}
        Prefix: {self.prefix}

        Called sub-function: {self.call_function}
        Deletions Requested: {len(self.proj_delete)}
        Additions requested: {len(self.proj_install)}

        Optional Flags:
        Risk Root: {self.risk}
        Only Pull: {self.pull}
        Don't Update: {self.stale}
        Verbose Debugging: {self.verbose}

        '''

def cli() -> DefConfig:
    '''
    Parse command line arguments
    '''
    description = '''
    NOTICE: This is only intended for "user" installs.
    CAUTION: DO NOT RUN THIS SCRIPT AS ROOT.
    CAUTION: If you still insist, I won't care.
    '''
    homedir = os.environ['HOME']
    parser = ArgumentParser(description=description,
                            formatter_class=RawDescriptionHelpFormatter)
    sub_parsers = parser.add_subparsers()
    list_gits = sub_parsers.add_parser(
        'list', aliases=['info'],
        help='display list of installed repositories and exit'
    )
    version = sub_parsers.add_parser('version', aliases=['ver'],
                                     help='display version and exit')
    parser.set_defaults(call_function=None)
    list_gits.set_defaults(call_function='info')
    version.set_defaults(call_function='version')
    parser.add_argument('-l', '--list', action='store_true', dest='info',
                        help='display list of installed repositories and exit')
    parser.add_argument('--version', action='store_true',
                        help='Display version and exit')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display list in verbose form')
    parser.add_argument('-s', '--stale', action='store_true',
                        help='skip updates, let the repository remain stale')
    parser.add_argument('-o', '--only-pull', action='store_true',
                        help='only pull, do not try to install')
    parser.add_argument('-f', '--force-risk', action='store_true', dest='risk',
                        help='force working with root permissions [DANGEROUS]')
    parser.add_argument(
        '-c', '--clone-dir', type=str, nargs='?', metavar='C_DIR',
        default=f'{homedir}/.pspman',
        help=f'Clone git repos in C_DIR/src [default: {homedir}/.pspman]'
    )
    parser.add_argument(
        '-p', '--prefix', type=str, nargs='?', metavar='PREFIX', default=None,
        help='path for installation [default: C_DIR]'
    )
    parser.add_argument(
        '-d', '--proj-delete', metavar='PROJ', type=str, nargs='*', default=[],
        help='PROJ to clone new project'
    )
    parser.add_argument(
        '-i', '--proj-install', metavar='URL', type=str, nargs='*', default=[],
        help='URL to clone new project'
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if args.info:
        setattr(args, 'call_function', 'info')
    if args.version:
        setattr(args, 'call_function', 'version')
    config = DefConfig()
    args_dict = vars(args)
    config.__dict__.update(vars(args))
    return config


CONFIG = cli()  # set configurations
'''
standard configuration
'''


def prepare_env(CONFIG: DefConfig) -> int:
    '''
    Check permissions and create prefix and source directories

    Returns:
        Error code

    '''
    perm_err = permission_check(CONFIG=CONFIG)
    if perm_err != 0:
        return perm_err
    os.makedirs(CONFIG.clone_dir, exist_ok=True)
    os.makedirs(CONFIG.prefix, exist_ok=True)
    return 0


def perm_pass(permdir: str) -> int:
    '''
    Args:
        permdir: directory whose permissions are to be checked

    Returns:
        Error code: ``1`` if all rwx permissions are not granted

    '''
    if not os.path.exists(permdir):
        # clone/prefix directory will be created anew
        permdir = os.path.split(os.path.realpath(permdir))[0]
    stdout = process_comm('stat', '-L', '-c', "%U %G %a",
                          permdir, fail_handle='report')
    if stdout is None:
        print('Error checking directory permissions, aborting...', mark=5)
        return 1
    owner, group, octperm = stdout.replace("\n", '').split(' ')
    if (octperm[-1] == '7') != 0:
        # everyone has access
        return 0
    if (octperm[-2] == '7') != 0:
        # some group has permissions
        stdout = process_comm('groups', os.environ['USER'],
                              fail_handle='report')
        if stdout is None:
            # error
            print('Error checking group permissions, aborting...', mark=5)
            return 1
        user_groups = stdout.split(' ')
        for u_grp in user_groups:
            if u_grp == group:
                return True
    if (octperm[-3] == '7') != 0:
        # owner has permissions
        if os.environ['USER'] == owner:
            return 0
    print('We do not have sufficient permissions', mark=5)
    print('Try another location', mark=2)
    print('Bye', mark=0)
    return 1


def permission_check(CONFIG: DefConfig) -> int:
    '''
    Check permissions in the given context

    Returns:
        Error code
    '''
    # Am I root?
    if os.environ['USER'].lower() == 'root':
        print('I hate dictators', mark=3)
        if not CONFIG.risk:
            print('Bye', mark=0)
            return 2
        print('I can only hope you know what you are doing...', mark=3)
        print('Here is a chance to kill me in', mark=2)
        timeout(10)
        print('', mark=0)
        print("¯\\_(ツ)_/¯ Your decision ¯\\_(ツ)_/¯", mark=3)
        print('', mark=0)
        print('Proceeding...', mark=1)
        err = 0  # Obviously!
    else:
        # Is installation directory read/writable
        err = perm_pass(CONFIG.clone_dir)
        err += perm_pass(CONFIG.prefix)
    return err
