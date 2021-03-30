#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This file is part of pspman.
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
Temporarily export a git group's profile (bin, lib, include, etc)
similar to python's venv
'''


import os
import sys
import typing
import subprocess
from tempfile import NamedTemporaryFile
from pathlib import Path
from . import CONFIG
from . import print as psprint


def inform_src(switch_src: str):
    '''
    Direct user how to switch to environment

    Args:
        switch_src: file to source
    '''
    psprint('Source-file ready.', mark='info')
    psprint()
    psprint("To activate,", mark='act')
    psprint('source ' + switch_src,
          pref='TYPE', short=False, text_color='lw', text_bgcol='k')
    psprint()
    psprint("To deactivate, close the terminal", mark='info')


def try_copy(switch_src: str) -> int:
    '''
    Try to copy the command 'source <switch_src>' to clipboard

    Args:
        switch_src: file to source

    Returns:
        Error during copy
    '''
    source_str = 'source ' + switch_src
    for clipboard in ('xcopy', 'wl-copy'):
        try:
            attempt = subprocess.Popen(clipboard, text=True,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
            attempt.communicate(input=source_str)
            return attempt.returncode
        except FileNotFoundError:
            pass
    return 127


def _munge(var_name: str, to_munge: typing.Union[str, Path],
           sep: str = ":") -> str:
    '''
    Add path to variable

    Args:
        var_name: name of variable to munge
        to_munge: Path to add to variable

    Returns:
        string to be sourced

    '''
    return var_name + '="' + str(to_munge) + sep + '${' + var_name + '}"'


def set_mod_env(switch_src: typing.IO[str], prefix: Path, name: str = None):
    '''
    Set write modified enviroment to file-handle switch_src

    Args:
        prefix: selected target prefix
        switch_src: temporary file-handle

    '''
    old_ps1 = os.environ.get('PS1')
    if name is not None:
        print(_munge('PS1', name), file=switch_src)
    print('GCC_EXEC_PREFIX="' + str(prefix) + '/"', file=switch_src)
    if prefix.joinpath('bin').is_dir():
        print(_munge('PATH', prefix.joinpath('bin')), file=switch_src)
    for bitbase in "", "64":
        lib = prefix.joinpath("lib" + bitbase)
        if lib.is_dir():
            print(_munge('PYTHONPATH',
                         lib.joinpath("python" +
                                      ".".join(sys.version.split(".")[:2]),
                                      'site-packages')),
                  file=switch_src)
            print(_munge('LD_LIBRARY_PATH', lib), file=switch_src)
            print(_munge('LIBRARY_PATH', lib), file=switch_src)
    include = prefix.joinpath('include')
    if include.is_dir():
        print(_munge('C_INCLUDE_PATH', include), file=switch_src)
        print(_munge('CPLUS_INCLUDE_PATH', include), file=switch_src)


def parse_prefix(prefix_str: str) -> typing.Tuple[typing.Optional[str],
                                                  typing.Optional[Path]]:
    '''
    parse and infer prefix
    '''
    if prefix_str in CONFIG.meta_db_dirs:
        # prefix is a grp_name
        prefix = CONFIG.meta_db_dirs[prefix_str].grp_path
        return prefix_str, prefix.resolve()
    for name, git_grp in CONFIG.meta_db_dirs.items():
        if str(git_grp.grp_path) == prefix_str:
            return name, git_grp.grp_path.resolve()
    if not prefix.is_dir():
        return None, None
    prefix = prefix.resolve()
    return prefix.name, prefix


def chenv(prefix_str: str, copy: bool = False) -> int:
    '''
    Create a temporary file that may be sourced to switch environment

    Args:
        prefix_str: name or path of prefix whose environment is to be added
        copy: try to copy the string 'source <filename>' to clipboard

    Returns:
        exit_code
    '''
    name, prefix = parse_prefix(prefix_str)
    if prefix is None:
        return 127
    with NamedTemporaryFile(mode='w', delete=False) as switch_src:
        set_mod_env(prefix=prefix, name=name, switch_src=switch_src)
    if not copy or try_copy(switch_src.name):
        inform_src(switch_src.name)
    return 0
