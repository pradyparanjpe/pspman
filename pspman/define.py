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
import shutil
import argcomplete
from psprint import print
from . import CONFIG
from .config import MetaConfig
from .classes import InstallEnv
from .tools import timeout


def cli(config: MetaConfig = None) -> argparse.ArgumentParser:
    '''
    Parse command line arguments

    Args:
        config: configuration to be modified by command line inputs

    Returns:
        modified ``confing``

    '''
    config = config or CONFIG
    description = '''

    \033[1;91mNOTICE: This is only intended for "user" packages.
    CAUTION: DO NOT RUN THIS SCRIPT AS ROOT.
    CAUTION: If you still insist, I won't care.\033[0m
    '''


    d_pref = config.data_dir
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawTextHelpFormatter
    )
    sub_parsers = parser.add_subparsers()
    version = sub_parsers.add_parser(name='version', aliases=['ver'],
                                     help='display version and exit')
    unlock = sub_parsers.add_parser(name='unlock', aliases=[],
                                    help='Unlock C_DIR and exit')
    list_gits = sub_parsers.add_parser(
        name='list', aliases=['info'],
        help='display list of cloned repositories and exit'
    )
    list_gits.add_argument('--meta', '-m', action='store_true',
                           help='List known C_DIR(s)')
    init = sub_parsers.add_parser(name='init', aliases=['initialize'],
                                  help='initialize pspman')
    goodbye = sub_parsers.add_parser(name='goodbye', aliases=['de-initialize'],
                                     help='Cleanup before uninstalling pspman')
    init.set_defaults(call_function='init')
    goodbye.set_defaults(call_function='goodbye')
    version.set_defaults(call_function='version')
    unlock.set_defaults(call_function='unlock')
    list_gits.set_defaults(call_function='info')
    parser.set_defaults(call_function=None)
    parser.add_argument('--init', action='store_true',
                        help='Initialize PSPMan')
    parser.add_argument('--version', action='store_true',
                        help='Display version and exit')
    parser.add_argument('-l', '--list', action='store_true', dest='info',
                        help='display list of cloned repositories and exit')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display verbose output')
    parser.add_argument('-s', '--stale', action='store_true',
                        help='skip updates, let repositories remain stale')
    parser.add_argument('-o', '--only-pull', action='store_true', dest='pull',
                        help='only pull, do not try to install')
    parser.add_argument('-f', '--force-risk', action='store_true', dest='risk',
                        help='force working with root permissions [DANGEROUS]')
    parser.add_argument('-p', '--prefix', type=str, nargs='?', metavar='PREF',
                        help=f'path for installation [default: {d_pref}]',
                        default=d_pref)
    parser.add_argument('-c', '--clone-dir', type=str, nargs='?', default=None,
                        metavar='C_DIR', help=f'''Clone git repos in C_DIR.
Please check if you want to add this to PATH.
[default: PREF{os.sep}src]
''')
    parser.add_argument('-d', '--delete', metavar='PROJ', type=str, nargs='*',
                        default=[], help='delete PROJ')
    parser.add_argument('-i', '--install', metavar='URL', type=str, nargs='*',
                        default=[],
        help=f'''
format: "URL[___branch[___'only'|___inst_argv[___sh_env]]]"

* *REMEMBER the QUOTATION MARKS*

* URL: url to be cloned.
* branch: custom branch to clone. Blank implies default.
* pull_only: 'true', 'only', 'pull', 'hold' => Don't try to install this URL
* inst_argv: Custom arguments. These are passed *raw* during installation.
* sh_env: VAR1=VAL1,VAR2=VAL2,VAR3=VAL3.... Modified install environment.

''')
    return parser


def cli_opts(config: MetaConfig = None) -> typing.Dict[str, typing.Any]:
    '''
    Parse cli arguments to return its dict
    '''
    config = config or CONFIG
    parser = cli()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if args.info:
        setattr(args, 'call_function', 'info')
    if hasattr(args, 'meta'):
        if args.meta:
            setattr(args, 'call_function', 'meta')
        else:
            setattr(args, 'call_function', 'info')
    if args.version:
        setattr(args, 'call_function', 'version')
    if args.init:
        setattr(args, 'call_function', 'init')
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
    stdout, err = subprocess.Popen(['stat', '-L', '-c', "%U %G %a", permdir],
                                   text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE).communicate()
    if err:
        print('Error checking directory permissions, aborting...', mark=5)
        return 1
    owner, group, octperm = stdout.replace("\n", '').split(' ')
    if (octperm[-1] == '7') != 0:
        # everyone has access
        return 0
    if (octperm[-2] == '7') != 0:
        # some group has permissions
        stdout, err = subprocess.Popen(['groups', user], text=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE).communicate()
        if err:
            # error
            print('Error checking group permissions, aborting...', mark=5)
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
        try:
            timeout(10)
        except:
            print("Aborting.", pref_color='g', pref=chr(0x1f197), short=False)
            return 1
        print()
        print("Your decision", pref=chr(0x1f937), pref_color='r',
              text_color="y", short=False)
        print()
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
    # lockfile is deliberately human-readable

    if os.path.exists(lockfile):
        # directory is locked
        if unlock:
            # restore all backup databases
            for filetype in "healthy", "fail":
                backup_file = os.path.join(env.clone_dir,
                                           f".pspman.{filetype}.yml")
                if os.path.isfile(backup_file + ".bak") and \
                   not os.path.isfile(backup_file):
                    os.rename(backup_file + ".bak", backup_file)
            temp_build = os.path.join(env.prefix, 'temp_build')
            if os.path.isdir(temp_build):
                shutil.rmtree(temp_build)
            os.remove(lockfile)
            return 1
        with open(lockfile, 'r') as lock_fh:
            print(f"Process with id {lock_fh.read()} is incomplete...", mark='err')
        print("Either wait for the process to get completed")
        print("OR interrupt the process and execute")
        print(f"pspman -c {os.path.split(env.clone_dir)[0]} unlock",
              mark='act')
        print("This WILL generally MESS UP source codes.", mark='warn')
        return 2
    if unlock:
        print(f'Lockfile {lockfile} not found.')
        return 2
    with open(lockfile, 'w') as lock_fh:
        lock_fh.write(str(os.getpid()))
    return 0
