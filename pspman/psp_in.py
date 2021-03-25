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
Read configuration

'''


import os
import typing
from pathlib import Path
import shutil
from .config import MetaConfig
from .errors import PathNameError


_PSPMAN_MARKERS = "### PSPMAN MOD ###"


def _sys_bash(sys_bash: typing.Union[str, os.PathLike] = None) -> Path:
    '''
    System-specific bashrc path

    Args:
        sys_bash: assert that it exists and return

    Returns:
        Path to system-bashrc

    '''
    if sys_bash:
        bash_path = Path(sys_bash)
        if bash_path.is_file():
            return bash_path.resolve()
        else:
            raise FileNotFoundError('Custom supplied bashrc file not found')
    if 'HOME' not in os.environ:
        raise FileNotFoundError('Default bashrc file not found')
    bash_path = Path(os.environ['HOME']).joinpath(".bashrc")
    return bash_path.resolve()


def _gen_sys_bash_text(psp_bash: str) -> str:
    '''
    Generate rc text content to redirect to pspman/bashrc file

    Args:
        psp_bash: path to config_dir/pspman/bashrc file

    '''
    if 'HOME' in os.environ:
        home_dir = Path(os.environ['HOME']).resolve()
        # Path relative to home, since this is personal
        # Such .bashrc can be synced between different users on same machine
        psp_bash = "${HOME}/" + str(Path(psp_bash)
                                    .resolve().relative_to(home_dir))
    shell_check_source = psp_bash.replace("${HOME}/", '')
    return "\n".join(('', _PSPMAN_MARKERS,
                      f'# shellcheck source="{shell_check_source}"',
                      f'if [[ -f "{psp_bash}" ]]; then',
                      '    # shellcheck disable=SC1091',
                      f'    . "{psp_bash}"; fi',
                      _PSPMAN_MARKERS, ''))


def _gen_psp_bash_text(data: Path) -> str:
    '''
    Generate text for bashrc modifier

    Args:
        data: path to data folder

    '''
    bin_path = data.joinpath('bin')
    py_path = data.joinpath('lib', '${python_ver}', 'site-packages')
    rc_text = (
        '# shellcheck shell=bash',
        '#-*- coding:utf-8; mode: shell-script -*-',
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


def _init_bash(psp_bash: Path, data_path: Path):
    '''
    Initiate bash rc

    Args:
        psp_bash: path to pspman's bashrc modifier
        data_path: path to default pspman data directory

    '''
    with open(psp_bash, 'w') as bashrc:
        bashrc.write(_gen_psp_bash_text(data_path))


def mod_bash(psp_bash: typing.Union[str, os.PathLike],
             sys_bash: typing.Union[str, os.PathLike] = None):
    '''
    Modify user's bashrc to include a reference to psp_bash

    Args:
        psp_bash: path to config_dir/pspman/bashrc file
        sys_bash: path to default bashrc
    '''
    mod_text = _gen_sys_bash_text(str(psp_bash))
    sys_bash = _sys_bash(sys_bash)
    if sys_bash.is_file():
        with open(sys_bash, 'r') as bashrc_h:
            rc_text = bashrc_h.read()
            if mod_text in rc_text:
                # already exported
                return
    if sys_bash.is_dir():
        raise IsADirectoryError(f'{sys_bash} should be a file, is a directory')
    with open(sys_bash, 'a') as bashrc_h:
        bashrc_h.write(mod_text)


def restore_bash(psp_bash: typing.Union[str, os.PathLike],
                 sys_bash: typing.Union[str, os.PathLike] = None) -> None:
    '''
    Restore bashrc

    Args:
        sys_bash: path to default bashrc
        psp_bash: path to config_dir/pspman/bashrc file

    '''
    sys_bash = _sys_bash(sys_bash)
    alteration = _gen_sys_bash_text(str(psp_bash))
    with open(sys_bash, 'r') as bashrc_h:
        rc_text = bashrc_h.read()
    if alteration not in rc_text:
        # pspman sections were already removed
        return
    rc_text = rc_text.replace(alteration, '')
    with open(sys_bash, 'w') as bashrc_h:
        bashrc_h.write(rc_text)


def de_init(config: MetaConfig,
            sys_bash: typing.Union[str, os.PathLike] = None):
    '''
    Undo changes made by init

    Args:
        config: PSPMan's configuration
        sys_bash: user's custom bashrc file

    '''
    sys_bash = _sys_bash(sys_bash)
    psp_bash = config.config_dir.joinpath('bashrc')
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
            instructions.append('# \033[0;94;40m' + 'rm -rf ' +
                                str(group_db.grp_path) + '\033[0m  # ' +
                                group_name)

    instructions.extend([
        '',
        "You may remove pspman configuration: run without '# '",
        '',
        f"# \033[1;97;40mrm -rf {config.config_dir}\033[0m",
        ''
    ])
    print('\n    '.join(instructions))


def init(config: MetaConfig, opt_in: typing.List[str] = None):
    '''
    Initialize environment, data structure for pspman

    Args:
        config: OS-specific configuration initialized by pspman

    '''

    opt_in = opt_in or []
    psp_config = config.config_dir.joinpath('config.yml')
    psp_bash = config.config_dir.joinpath('bashrc')
    mod_bash(psp_bash)
    if not psp_bash.is_file():
        if psp_bash.is_dir():
            # Thou Shallt be a file
            shutil.rmtree(psp_bash)
    _init_bash(psp_bash, config.data_dir)

    if not psp_config.is_file():
        if psp_config.is_dir():
            # Thou Shallt be a file
            shutil.rmtree(psp_config)
    dep_fail = False

    for dependency in 'python3', 'git', 'pip', *opt_in:
        avail = shutil.which(dependency)
        if avail is None:
            print(f"Dependency not found: {dependency}")
            dep_fail = True
    if dep_fail:
        print("Unless all dependencies are installed, pspman shall fail")
        return 1
    return 0
