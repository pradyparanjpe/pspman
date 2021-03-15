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

# install pspman


import os
import sys
import subprocess


PSPMAN_MARKERS = "### PSPMAN MOD ###"
'''
Markers that separate PSPMAN modifications from rest of code
'''


MOD_BASH = '''%s
if [[ -n ${XDG_CONFIG_HOME} ]]; then
    if [[ -f "${XDG_CONFIG_HOME}/pspman/bashrc" ]]; then
        . "${XDG_CONFIG_HOME}/pspman/bashrc";
    fi
else
    if [[ -f "${HOME}/.config/pspman/bashrc" ]]; then
        . "${HOME}/.config/pspman/bashrc";
    fi
fi
%s
''' % (PSPMAN_MARKERS, PSPMAN_MARKERS)
'''
Redirect to ${XDG_CONFIG_HOME}/pspman/bashrc

'''


def restore_bash() -> None:
    '''
    Restore bashrc file
    '''
    bashrc_path = os.environ['HOME'] + '/.bashrc'
    with open(bashrc_path, 'r') as bashrc_h:
        rc_text = bashrc_h.read()
    rc_parts = rc_text.split(PSPMAN_MARKERS)
    if (len(rc_parts) - 1) % 2 != 0:
        # incomplete MOD_BASH
        print("PSPMAN section in bashrc file was modified incorrectly.")
        print(f"Please erase the relavent section, marked by {PSPMAN_MARKERS}")
        print(f"in file: {bashrc_path}")
    elif len(rc_parts) - 1 == 0:
        # PSPMAN sections were removed
        return
    rc_text = "".join(rc_parts[::2])
    with open(bashrc_path, 'w') as bashrc_h:
        bashrc_h.write(rc_text)


def gen_mod_bash() -> str:
    '''
    Generate text for bashrc modifier

    '''
    rc_text = []
    rc_text.append('''
python_ver=$(python --version |cut -d "." -f1,2 |sed 's/ //' |sed 's/P/p/')
''')
    bin_path = '${HOME}/.pspman/bin'
    py_path = '${HOME}/.pspman/lib/${python_ver}/site-packages'
    rc_text.append('''
if [[ ! ${PATH} =~ %s ]]; then
    PATH="%s:$PATH"
fi
''' % (bin_path, bin_path))

    rc_text.append('''
if [[ ! ${PYTHONPATH} =~ %s ]]; then
    PYTHONPATH="%s:${PYTHONPATH}"
fi
''' % (py_path, py_path))

    rc_text.append('''
export PATH;
export PYTHONPATH;
''')
    return "\n".join(rc_text)


def chg_bashrc() -> None:
    '''
    Add environment variables

    '''
    # Linux/Mac
    dir_struct = "bin", "share", "lib", "lib64", "include", "etc", "tmp", "src"
    for workdir in dir_struct:
        os.makedirs(os.environ['HOME'] + '/.pspman/' + workdir,
                    exist_ok=True)

    config_d = os.environ.get("XDG_CONFIG_HOME",
                              os.environ['HOME'] + "/.config/pspman")
    os.makedirs(config_d, exist_ok=True)
    with open(f"{config_d}/bashrc", 'w') as mod_bash_h:
        mod_bash_h.write(gen_mod_bash())

    bashrc_path = os.environ['HOME'] + '/.bashrc'
    if os.path.isfile(bashrc_path):
        with open(bashrc_path, 'r') as bashrc_h:
            rc_text = bashrc_h.read()
            if MOD_BASH in rc_text:
                return
    with open(bashrc_path, 'a') as bashrc_h:
        bashrc_h.write(MOD_BASH)


def get_pspman():
    '''
    Install pspman

    '''
    print("installing pspman")
    subprocess.Popen([
        'python3', '-m', 'pip', 'install', '--prefix',
        os.path.join(os.environ['HOME'], '.pspman'), '-U', 'pspman'
    ])


def install():
    '''
    Installation
    '''
    chg_bashrc()
    get_pspman()


def uninstall():
    '''
    Uninstallation
    '''
    restore_bash()
    home_dir = os.environ['HOME']
    instructions = []
    instructions.append('''
    If you wish, erase standard .pspman folder: type without '# ':'''
    )

    instructions.append(f"\033[1;97;40m# rm -rf {home_dir}/.pspman\033[0m")
    instructions.append("")
    instructions.append(
    '''... and similarly, any other C_DIR created by -c flag

    You may remove pspman configuration:'''
    )

    conf_dir = os.environ.get('XDG_CONFIG_HOME',
                              os.environ['HOME'] + "/.config") + "/pspman"
    instructions.append(f"\033[1;97;40mrm -rf {conf_dir}\033[0m")
    instructions.append("")
    print('\n    '.join(instructions))


def main() -> None:
    '''
    Main subroutine

    '''
    if sys.argv[-1] == 'doinstall':
        install()
    elif sys.argv[-1] == 'douninstall':
        uninstall()
    else:
        print("Calling this script from the terminal is useless")
        print("This script is used by `install.sh` script")

if __name__ == "__main__":
    main()
