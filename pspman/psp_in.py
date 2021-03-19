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
Read configuration

'''


import os
import typing
import subprocess
import shutil
import yaml
from .config import MetaConfig
from .errors import PathNameError


_PSPMAN_MARKERS = "### PSPMAN MOD ###"


def _sys_bash(path: str = None) -> str:
    '''
    System-specific path

    Args:
        path: assert that path exists and return

    Returns:
        Path to system-bashrc

    '''
    if path:
        if os.path.isfile(path):
            return path
        else:
            raise FileNotFoundError('Custom supplied bashrc file not found')
    if 'HOME' not in os.environ:
        raise FileNotFoundError('Default bashrc file not found')
    path = os.path.join(os.environ['HOME'], ".bashrc")
    return path


def _gen_sys_bash_text(psp_bash: str) -> str:
    '''
    Generate rc text content to redirect to pspman/bashrc file

    Args:
        psp_bash: path to config_dir/pspman/bashrc file

    '''
    return "\n".join(('', _PSPMAN_MARKERS,
                           f'if [[ -f "{psp_bash}" ]]; then',
                           f'    . "{psp_bash}"; fi',
                           _PSPMAN_MARKERS, ''))


def _gen_psp_bash_text(data_path: str) -> str:
    '''
    Generate text for bashrc modifier

    '''
    bin_path = os.path.join(data_path, 'bin')
    py_path = os.path.join(data_path, 'lib', '${python_ver}', 'site-packages')
    rc_text = (
        '# shellcheck shell=bash',
        "#-*- coding:utf-8; mode: shell-script -*-",
        '',
        "python_ver=\"$(python3 --version " +
        "| cut -d '.' -f1,2 " +
        "| sed 's/ //' " +
        "| sed 's/P/p/')\"",
        '',
        f'pspbin_path="{bin_path}"',
        f'psppy_path="{py_path}"',
        'if [[ ! "${PATH}" =~ ${pspbin_path} ]]; then',
        '    PATH="${pspbin_path}:${PATH}";',
        'fi;',
        ''
        'if [[ ! "${PYTHONPATH}" =~ ${psppy_path} ]]; then',
        '    PYTHONPATH="${psppy_path}:${PYTHONPATH}";',
        'fi;',
        '',
        'export PATH;',
        'export PYTHONPATH;'
    )
    return "\n".join(rc_text)


def _init_bash(psp_bash: str, data_path: str):
    '''
    Initiate bash rc

    Args:
        psp_bash: path to pspman's bashrc modifier
        data_path: path to default pspman data directory

    '''
    with open(psp_bash, 'w') as bashrc:
        bashrc.write(_gen_psp_bash_text(data_path))


def mod_bash(psp_bash: str, sys_bash: str = None):
    '''
    Modify user's bashrc to include a reference to psp_bash

    Args:
        psp_bash: path to config_dir/pspman/bashrc file
        sys_bash: path to default bashrc
    '''
    mod_text = _gen_sys_bash_text(psp_bash)
    sys_bash = _sys_bash(sys_bash)
    if os.path.isfile(sys_bash):
        with open(sys_bash, 'r') as bashrc_h:
            rc_text = bashrc_h.read()
            if mod_text in rc_text:
                # already exported
                return
    if os.path.isdir(sys_bash):
        raise IsADirectoryError(f'{sys_bash} should be a file, is a directory')
    with open(sys_bash, 'a') as bashrc_h:
        bashrc_h.write(mod_text)


def restore_bash(psp_bash: str, sys_bash: str = None) -> None:
    '''
    Restore bashrc

    Args:
        sys_bash: path to default bashrc
        psp_bash: path to config_dir/pspman/bashrc file

    '''
    sys_bash =  _sys_bash(sys_bash)
    alteration = _gen_sys_bash_text(psp_bash)
    with open(sys_bash, 'r') as bashrc_h:
        rc_text = bashrc_h.read()
    if alteration not in rc_text:
        # pspman sections were already removed
        return
    rc_text = rc_text.replace(alteration, '')
    with open(sys_bash, 'w') as bashrc_h:
        bashrc_h.write(rc_text)


def de_init(config: MetaConfig, sys_bash: str = None):
    '''
    Undo changes made by init

    Args:
        config: PSPMan's configuration
        sys_bash: user's custom bashrc file

    '''
    sys_bash = _sys_bash(sys_bash)
    psp_bash = os.path.join(config.config_dir, 'bashrc')
    restore_bash(psp_bash, sys_bash)
    instructions = [
        '',
        'If you wish, erase the default pspman base: type without \'# \':',
        f"# \033[1;97;40mrm -rf {config.data_dir}\033[0m",
        '',
        'and similarly, any other C_DIR created by -c flag, listed below:'
        ''
    ]
    del config.meta_db_dirs['default']
    if len(config.meta_db_dirs) == 0:
        instructions.append("[\033[1;31;40mNone\033[0m]")
    else:
        for group_name, group_db in config.meta_db_dirs.items():
            instructions.append('# \033[0;94;40m' + 'rm -rf ' + group_db.path +
                                '\033[0m  # ' + group_name)

    instructions.extend([
        '',
        "You may remove pspman configuration: run without '# '",
        '',
        f"# \033[1;97;40mrm -rf {config.config_dir}\033[0m",
        ''
    ])
    print('\n    '.join(instructions))


def init(config: MetaConfig):
    '''
    Initialize environment, data structure for pspman

    Args:
        config: OS-specific configuration initialized by pspman

'''

    psp_config = os.path.join(config.config_dir, 'config.yml')
    psp_bash = os.path.join(config.config_dir, 'bashrc')
    mod_bash(psp_bash)
    if not os.path.isfile(psp_bash):
        if os.path.isdir(psp_bash):
            # Thou Shallt be a file
            shutil.rmtree(psp_bash)
    _init_bash(psp_bash, config.data_dir)

    if not os.path.isfile(psp_config):
        if os.path.isdir(psp_config):
            # Thou Shallt be a file
            shutil.rmtree(psp_config)
    dep_fail = False
    for dependency in 'python3', 'pip', 'git' , 'make', 'cmake', 'meson', 'go':
        avail = shutil.which(dependency)
        if avail is None:
            print(f"Dependency not found: {dependency}")
            dep_fail = True
    if dep_fail:
        print("Unless all dependencies are installed, pspman shall fail")
        return 1
    return 0
