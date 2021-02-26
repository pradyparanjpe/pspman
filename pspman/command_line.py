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
from .project_actions import (del_proj, list_proj, git_pulls,
                              find_gits, add_git)
from .installations import auto_install, report_failures
from . import print


def cli() -> typing.Dict[str, object]:
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
    parser.add_argument('-f', '--force-root', action='store_true',
                        help='force working with root permissions [DANGEROUS]')
    parser.add_argument('-s', '--stale', action='store_true',
                        help='skip updates, let the repository remain stale')
    parser.add_argument('-l', '--list-projs', action='store_true',
                        help='display list of installed repositories and exit')
    parser.add_argument('-o', '--only-pull', action='store_true',
                        help='only pull, do not try to install')
    parser.add_argument('-c', '--clone-dir', type=str, nargs="?",
                        default=f'{homedir}/.pspman/programs',
                        help='path for all git clones')
    parser.add_argument('-p', '--prefix', type=str, nargs="?",
                        default=f'{homedir}/.pspman',
                        help='path for installation')
    parser.add_argument('-i', '--pkg-install', metavar='URL', type=str,
                        nargs="*", help='URL to clone new project', default=[])
    parser.add_argument('-d', '--pkg-delete', metavar='PROJ', type=str,
                        nargs="*", help='PROJ to clone new project',
                        default=[])
    argcomplete.autocomplete(parser)
    args = vars(parser.parse_args())
    return args


def call() -> None:
    '''
    Parse command line arguments to

        * list cloned git repositories,
        * add / remove git repositories and corresponding installations
        * pull git repositories,
        * update (default),

    '''
    args = cli()
    pkg_grp = InstallEnv(
        clonedir=args.get('clone_dir'),
        prefix=args.get('prefix'),
        pkg_install=args.get("pkg_install", []),
        pkg_delete=args.get("pkg_delete", ""),
        stale=args.get('stale', False),
        force_root=args.get('force_root'),
        only_pull=args.get('only_pull'),
    )
    find_gits(pkg_grp)
    list_proj(
        env=pkg_grp,
        display=args.get('list_projs', False),
        grace_exit=not(
            not args.get('list_projs') or args.get('only_pull', False)
            or args.get('pkg_delete', []) or args.get('pkg_install', [])
        )
    )
    del_proj(pkg_grp)
    git_pulls(pkg_grp)
    add_git(pkg_grp)
    if not args.get('only_pull'):
        auto_install(pkg_grp)
    print("done.", mark=1)
