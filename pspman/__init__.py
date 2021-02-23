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

import os
import sys
from psprint import DEFAULT_PRINT
from .command_line import cli


# Configure DEFAULT_PRINT
DEFAULT_PRINT.switches['pad'] = True
DEFAULT_PRINT.print_kwargs['flush'] = True
DEFAULT_PRINT.switches['short'] = False
print = DEFAULT_PRINT.psprint


def call() -> None:
    '''
    Parse command line arguments to
    perform update (default),
    pull git repositories,
    list cloned git repositories,
    add / remove git repositories and corresponding installations
    '''
    args = cli()
    from .classes import InstallEnv
    pkg_grp = InstallEnv(
        clonedir=args.get('clone_dir'),
        prefix=args.get('prefix'),
        pkg_install=args.get("pkg_install", []),
        pkg_delete=args.get("pkg_delete", ""),
        stale=args.get('stale', False),
        force_root=args.get('force_root'),
        only_pull=args.get('only_pull'),
    )
    pkg_grp.find_gits()
    pkg_grp.list_proj(display=args.get('list_projs', False),
                      grace_exit=not(args.get('only_pull', False)
                                     or args.get('pkg_delete', [])
                                     or args.get('pkg_install', [])
                                     or not args.get('list_projs'))
                      )
    pkg_grp.del_proj()
    pkg_grp.git_pulls()
    pkg_grp.new_install()
    pkg_grp.auto_install()
    os.chdir(pkg_grp.base_dir)
    print("done.", mark=1)
    sys.exit(0)


__version__ = '21.2.23'
