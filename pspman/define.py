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
import sys
import typing
import subprocess
import argparse
import argcomplete
from psprint import print
from .classes import InstallEnv
from .tools import timeout


def cli() -> argparse.ArgumentParser:
    '''
    Parse command line arguments

    Args:
        config: configuration to be modified by command line inputs

    Returns:
        modified ``confing``

    '''
    description = '''

    \033[1;91mNOTICE: This is only intended for "user" packages.
    CAUTION: DO NOT RUN THIS SCRIPT AS ROOT.
    CAUTION: If you still insist, I won't care.\033[0m
    '''


    homedir = os.environ['HOME']
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )
    sub_parsers = parser.add_subparsers()
    list_gits = sub_parsers.add_parser(
        'list', aliases=['info'],
        help='display list of installed repositories and exit'
    )
    version = sub_parsers.add_parser('version', aliases=['ver'],
                                     help='display version and exit')
    unlock = sub_parsers.add_parser('unlock', aliases=[],
                                     help='unlock C_DIR and exit')
    unlock.set_defaults(call_function='unlock')
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
                        help='only pull, do not try to install',
                        dest='pull')
    parser.add_argument('-f', '--force-risk', action='store_true', dest='risk',
                        help='force working with root permissions [DANGEROUS]')
    parser.add_argument(
        '-p', '--prefix', type=str, nargs='?', metavar='PREFIX',
        default=os.path.join(homedir, ".pspman"),
        help='path for installation ' +
        f'[default: {os.path.join(homedir, ".pspman")}]')
    parser.add_argument(
        '-c', '--clone-dir', type=str, nargs='?', metavar='C_DIR',
        default=None,
        help=f'''Clone git repos in C_DIR. Is it exported with PATH
        [default: PREFIX{os.sep}src]
        '''
    )
    parser.add_argument(
        '-d', '--delete', metavar='PROJ', type=str, nargs='*', default=[],
        help='delete PROJ'
    )
    parser.add_argument(
        '-i', '--install', metavar='URL', type=str, nargs='*', default=[],
        help=f'''
format: "URL[[[[___branch]___inst_argv]___sh_env]___'only']"

* REMEMBER the QUOTATION MARKS *

* URL: url to be cloned.
* branch: custom branch to clone blank implies default.
* inst_argv: custom arguments these are passed raw.
* sh_env: VAR1=VAL1,VAR2=VAL2,VAR3=VAL3....
* pull_only: 'True', 'only', 'pull', 'hold' => Don't try to install this URL

'''
    )
    return parser


def cli_opts() -> typing.Dict[str, typing.Any]:
    '''
    Parse cli arguments to return its dict
    '''
    parser = cli()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if args.info:
        setattr(args, 'call_function', 'info')
    if args.version:
        setattr(args, 'call_function', 'version')
    return vars(args)


def perm_pass(env: InstallEnv, permdir: str) -> int:
    '''
    Args:
        permdir: directory whose permissions are to be checked

    Returns:
        Error code: ``1`` if all rwx permissions are not granted

    '''
    if env.verbose:
        print(f'Checking permissions for {permdir}')
    while not os.path.exists(permdir):
        # clone/prefix directory get be created anew
        permdir = os.path.split(os.path.realpath(permdir))[0]
        if env.verbose:
            print(f'Checking permissions for the parent: {permdir}')
    user = os.environ.get('USER', 'root')
    stdout, stderr = subprocess.Popen(
        ['stat', '-L', '-c', "%U %G %a", permdir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True
    ).communicate()
    if stderr:
        print('Error checking directory permissions, aborting...',
              mark=5)
        return 1
    owner, group, octperm = stdout.replace("\n", '').split(' ')
    if (octperm[-1] == '7') != 0:
        # everyone has access
        return 0
    if (octperm[-2] == '7') != 0:
        # some group has permissions
        stdout, stderr = subprocess.Popen(
            ['groups', user], text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).communicate()
        if stderr:
            # error
            print('Error checking group permissions, aborting...',
                  mark=5)
            return 1
        user_groups = stdout.split(' ')
        for u_grp in user_groups:
            if u_grp == group:
                return 0
    if (octperm[-3] == '7') != 0:
        # owner has permissions
        if user == owner:
            return 0
    print(f'''
    We [{user}] do not have sufficient permissions [{octperm}]
    on {owner}'s directory: {permdir}
    ''', mark=5)
    print('Try another location', mark=2)
    return 1


def prepare_env(env: InstallEnv) -> int:
    '''
    Check permissions and create prefix and source directories

    Returns:
        Error code
    '''
    # Am I root?
    if os.environ.get('USER', 'root').lower() == 'root':
        print('I hate dictators', mark=3)
        if not env.risk:
            print('Bye', mark=0)
            return 2
        print('I can only hope you know what you are doing...',
              mark=3)
        print('Here is a chance to kill me in', mark=2)
        timeout(10)
        print('', mark=0)
        print("¯\\_(ツ)_/¯ Your decision ¯\\_(ツ)_/¯", mark=3)
        print('', mark=0)
        print('Proceeding...', mark=1)
    else:
        # Is installation directory read/writable
        err = perm_pass(env=env, permdir=env.clone_dir)
        err += perm_pass(env=env, permdir=env.prefix)
        if err != 0:
            print('Bye', mark=0)
            return err
    os.makedirs(env.clone_dir, exist_ok=True)
    os.makedirs(env.prefix, exist_ok=True)
    return 0


def lock(env: InstallEnv, unlock: bool = False):
    '''
    Unlock up the directory

    Args:
        env: installation context
        unlock: unlock existing locks?

    Returns:
        Error code

    '''
    lockfile = os.path.join(env.clone_dir, '.proc.lock')
    if os.path.exists(lockfile):
        # directory is locked
        if unlock:
            os.remove(lockfile)
            return 0
        with open(lockfile, 'r') as lock_fh:
            print(f"Process with id {lock_fh.read()} is incomplete...",
                  mark='err')
        print("Either wait for the process to get completed")
        print("OR interrupt the process and execute")
        print(f"pspman -c {os.path.split(env.clone_dir)[0]} unlock",
              mark='act')
        print("This WILL generally MESS UP source codes.", mark='warn')
        return 1
    if unlock:
        print(f'Lockfile {lockfile} not found.')
        return 1
    with open(lockfile, 'w') as lock_fh:
        lock_fh.write(str(os.getpid()))
    return 0
