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


def _sys_profile(sys_profile: typing.Union[str, os.PathLike] = None) -> Path:
    '''
    System-specific profile path

    Args:
        sys_profile: assert that it exists and return

    Returns:
        Path to system-profile

    '''
    if sys_profile:
        profile_path = Path(sys_profile)
        if profile_path.is_file():
            return profile_path.resolve()
        else:
            raise FileNotFoundError('Custom supplied profile file not found')
    if 'HOME' not in os.environ:
        raise FileNotFoundError('Default profile file not found')
    profile_path = Path(os.environ['HOME']).joinpath(".profile")
    return profile_path.resolve()


def _gen_sys_profile_text(psp_profile: str) -> str:
    '''
    Generate rc text content to redirect to pspman/profile file

    Args:
        psp_profile: path to config_dir/pspman/profile file

    '''
    if 'HOME' in os.environ:
        home_dir = Path(os.environ['HOME']).resolve()
        # Path relative to home, since this is personal
        # Such .profile can be synced between different users on same machine
        psp_profile = "${HOME}/" + str(Path(psp_profile)
                                       .resolve().relative_to(home_dir))
        shell_check_source = psp_profile.replace("${HOME}/", '')
    return "\n".join(('', _PSPMAN_MARKERS,
                      f'# shellcheck source="{shell_check_source}"',
                      f'if [[ -f "{psp_profile}" ]]; then',
                      '    # shellcheck disable=SC1091',
                      f'    . "{psp_profile}"; fi',
                      _PSPMAN_MARKERS, ''))


def _gen_psp_profile_text(data: Path) -> str:
    '''
    Generate text for profile modifier

    Args:
        data: path to data folder

    '''
    bin_path = data.joinpath('bin')
    py_path = data.joinpath('lib', '${python_ver}', 'site-packages')
    rc_text = (
        '# shellcheck shell=sh',
        '#-*- coding:utf-8; mode: shell-script -*-',
        '',
        "python_ver=\"$(python3 --version " +
        "| cut -d '.' -f1,2 " +
        "| sed 's/ //' " +
        "| sed 's/P/p/')\"",
        '',
        f'pspbin_path="{bin_path}"',
        f'psppy_path="{py_path}"',
        'if [ "${PATH#*${pspbin_path}}" = "${PATH}" ]; then',
        '    PATH="${pspbin_path}:${PATH}";',
        'fi;',
        ''
        'if [ "${PYTHONPATH#*${psppy_path}}" = "${PYTHONPATH}" ]; then',
        '    PYTHONPATH="${psppy_path}:${PYTHONPATH}";',
        'fi;',
        '',
        'export PATH;',
        'export PYTHONPATH;'
    )
    return "\n".join(rc_text)


def _init_profile(psp_profile: Path, data_path: Path):
    '''
    Initiate profile rc

    Args:
        psp_profile: path to pspman's profile modifier
        data_path: path to default pspman data directory

    '''
    with open(psp_profile, 'w') as profile:
        profile.write(_gen_psp_profile_text(data_path))


def _shell_inform(sys_profile: Path):
    '''
    Inform about discovered shell login profiles
    '''
    home_dir = Path(os.environ['HOME'])
    known_profiles = {
        'bash': ('bash_profile', 'bash_login'),
        'zsh': ('zprofile', 'zlogin'),
        'generic': ('login'),
    }
    found_profiles = {}

    for shell, loginits in known_profiles.items():
        for profile in loginits:
            profile_path = home_dir.joinpath("." + profile)
            if profile_path.exists():
                found_profiles[shell] = profile_path.resolve()
                break

    if not found_profiles:
        return

    inform = ['', 'Following shell: profiles were found.']
    for shell, profile_path in found_profiles.items():
        inform.append(f"{shell}: {str(profile_path)}")

    inform.extend((
        '',
        f'Confirm that they inherit from {str(sys_profile.resolve())}',
        '',
        "e.g. by adding the following lines without '# '",
        '',
        '# \033[0;97;40mif [ -f "${HOME}"/.profile ]; then\033[m',
        '# \033[0;97;40m    . "${HOME}"/.profile\033[m',
        '# \033[0;97;40mfi\033[m',
        '',
    ))
    print('\n    '.join(inform))


def mod_profile(psp_profile: typing.Union[str, os.PathLike],
                sys_profile: typing.Union[str, os.PathLike] = None):
    '''
    Modify user's profile to include a reference to psp_profile

    Args:
        psp_profile: path to config_dir/pspman/profile file
        sys_profile: path to default profile
    '''
    mod_text = _gen_sys_profile_text(str(psp_profile))
    sys_profile = _sys_profile(sys_profile)
    if sys_profile.is_file():
        with open(sys_profile, 'r') as profile_h:
            rc_text = profile_h.read()
            if mod_text in rc_text:
                # already exported
                return
    if sys_profile.is_dir():
        raise IsADirectoryError(
            f'{sys_profile} should be a file, is a directory'
        )
    with open(sys_profile, 'a') as profile_h:
        profile_h.write(mod_text)

    _shell_inform(sys_profile)

def restore_profile(psp_profile: typing.Union[str, os.PathLike],
                    sys_profile: typing.Union[str, os.PathLike]
                    = None) -> None:
    '''
    Restore profile

    Args:
        sys_profile: path to default profile
        psp_profile: path to config_dir/pspman/profile file

    '''
    sys_profile = _sys_profile(sys_profile)
    alteration = _gen_sys_profile_text(str(psp_profile))
    with open(sys_profile, 'r') as profile_h:
        rc_text = profile_h.read()
    if alteration not in rc_text:
        # pspman sections were already removed
        return
    rc_text = rc_text.replace(alteration, '')
    with open(sys_profile, 'w') as profile_h:
        profile_h.write(rc_text)


def de_init(config: MetaConfig,
            sys_profile: typing.Union[str, os.PathLike] = None):
    '''
    Undo changes made by init

    Args:
        config: PSPMan's configuration
        sys_profile: user's custom profile file

    '''
    sys_profile = _sys_profile(sys_profile)
    psp_profile = config.config_dir.joinpath('profile')
    restore_profile(psp_profile, sys_profile)
    instructions = [
        '',
        'If you wish, erase the default pspman base: type without \'# \':',
        f"# \033[1;97;40mrm -rf {config.data_dir}\033[m",
        '',
        'and similarly, any other C_DIR created by -c flag, listed below:'
        ''
    ]
    del config.meta_db_dirs['default']
    if len(config.meta_db_dirs) == 0:
        instructions.append("[\033[1;31;40mNone\033[m]")
    else:
        for group_name, group_db in config.meta_db_dirs.items():
            instructions.append('# \033[0;94;40m' + 'rm -rf ' +
                                str(group_db.grp_path) + '\033[m  # ' +
                                group_name)
    instructions.extend((
        '',
        "You may remove pspman configuration: run without '# '",
        '',
        f"# \033[1;97;40mrm -rf {config.config_dir}\033[m",
        ''
    ))
    print('\n    '.join(instructions))


def init(config: MetaConfig, opt_in: typing.List[str] = None):
    '''
    Initialize environment, data structure for pspman

    Args:
        config: OS-specific configuration initialized by pspman

    '''

    opt_in = opt_in or []
    psp_config = config.config_dir.joinpath('config.yml')
    psp_profile = config.config_dir.joinpath('profile')
    mod_profile(psp_profile)
    if not psp_profile.is_file():
        if psp_profile.is_dir():
            # Thou Shallt be a file
            shutil.rmtree(psp_profile)
        _init_profile(psp_profile, config.data_dir)

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


def init_banner():
    '''
    Banner to display after init
    '''
    banner = [
        '',
        '\033[0;92;40mPSPMan has been initialized.\033[m',
        '',
        "To point the location of PSPMan for your shell, Type without '# ':",
        '',
        "# \033[1;97;40msource ${HOME}/.profile\033[m",
        'for the \33[94;40mcurrent\33[m and each new terminal',
        'to avoid the following error:',
        '\033[0;31;40mpspman: command not found\033[m',
        '',
        "Typing 'source ...' is not required after the next login.",
        "After the next login, if the above error is encountered, then",
        'confirm that .profile is inherited by the shell.',
        '',
    ]
    print('\n    '.join(banner))
