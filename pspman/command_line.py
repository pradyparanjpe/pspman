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
input/outputs
'''


import os
import typing
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import argcomplete
from .classes import InstallEnv
from .project_actions import CurrentActions
from . import print


def cli() -> typing.Dict[str, typing.Any]:
    '''
    Parse command line arguments
    '''
    description = '''
    NOTICE: This is only intended for "user" installs.
    CAUTION: DO NOT RUN THIS SCRIPT AS ROOT.
    CAUTION: If you still insist, I won't care.
    '''
    homedir = os.environ["HOME"]
    parser = ArgumentParser(description=description,
                            formatter_class=RawDescriptionHelpFormatter)
    sub_parsers = parser.add_subparsers()
    list_gits = sub_parsers.add_parser('list', aliases=['info'])
    list_gits.set_defaults(call_function='list')
    # add_gits = sub_parsers.add_parser('add', aliases=['install'])
    # del_gits = sub_parsers.add_parser('delete', aliases=['remove','uninstall'])
    parser.add_argument('-c', '--clone-dir', type=str, nargs="?",
                        default=f'{homedir}/.pspman/programs',
                        help='path for all git clones')
    parser.add_argument('-p', '--prefix', type=str, nargs="?",
                        default=f'{homedir}/.pspman',
                        help='path for installation')
    parser.add_argument('-l', '--list-projs', action='store_true',
                        help='display list of installed repositories and exit')
    parser.add_argument('-s', '--stale', action='store_true',
                        help='skip updates, let the repository remain stale')
    parser.add_argument('-o', '--only-pull', action='store_true',
                        help='only pull, do not try to install')
    parser.add_argument('-f', '--force-risk', action='store_true',
                        help='force working with root permissions [DANGEROUS]')
    # parser.add_argument('-i', '--pkg-install', metavar='URL', type=str,
                        # nargs="*", help='URL to clone new project', default=[])
    # parser.add_argument('-d', '--pkg-delete', metavar='PROJ', type=str,
                        # nargs="*", help='PROJ to clone new project',
                        # default=[])
    argcomplete.autocomplete(parser)
    args = vars(parser.parse_args())

    # Pack choices
    choices = {
        'stale': args.get('stale', False),
        'only_pull': args.get('only_pull', False),
        'force_risk': args.get('force_risk', False),
    }
    del args['stale']
    del args['only_pull']
    del args['force_risk']
    args['choices'] = choices
    return args


def list(env: InstallEnv) -> None:
    '''
    List all known gits

    '''

def call() -> None:
    '''
    Parse command line arguments to

        * list cloned git repositories,
        * add / remove git repositories and corresponding installations
        * pull git repositories,
        * update (default),

    '''
    args = cli()
    action = CurrentActions(
        clone_dir=args['clone_dir'],
        prefix=args.get('prefix'),
        choices=args['choices'],
    )
    sub_call = args.get('call_function')
    if sub_call is not None:
        {'list': action.list_project}[sub_call]()
    else:
        print('no subfunction called', mark='bug' )
    action.update_project()
    print("Trying installations")
    action.install_project()
    action.save_db()
    print("done.", mark=1)
