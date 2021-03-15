#!/usr/bin/env bash
# -*- coding:utf-8; mode:shell-script -*-
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


function background_check() {
    if test "command -v pspman >> /dev/null"; then
        echo -e "
        \033[0;91mPSPMAN is already installed:\033[0m
        $( pspman version ) .


        \033[0;94mIf you wish to install afresh...\033[0m

        1) Uninstall pspman using \033[1;97;40mpip\033[0m: type without '# ':

        \033[0;97;40m# until ! command -v pspman >/dev/null; \
do pip uninstall -y pspman >/dev/null; done\033[0m

        2) Remove pspman clone from its standard location: type without '# ':

        \033[0;97;40m# rm -rf \"${HOME}/.pspman/src/pspman\"\033[0m

        ... and initiate installation again:

        I am aborting for now without making any changes.
"
        exit 1
    fi

    if [[ ! -f "./_install.py" ]]; then
        echo "pspman/_install.py wasn't found. Downloading..."
        wget "https://raw.githubusercontent.com/pradyparanjpe/\
pspman/master/install_scripts/_install.py"
    fi
}


function get_pip() {
    if ! test "$(command -v pip)"; then
        wget "https://bootstrap.pypa.io/get-pip.py"
        python3 "get-pip.py" --user
        rm get-pip.py
    fi
    echo "Updating pip"
    python3 -m "pip" install --user -U pip setuptools wheel
}

function install() {
    background_check $@
    if ! test "$(command -v python)"; then
        echo "Please install python3 first"
        exit 1
    fi
    get_pip
    python3 ./_install.py doinstall
    echo "Updating Pspman"
    python3 -m pspman -s -i https://github.com/pradyparanjpe/pspman.git
    python3 -m pip install --prefix "${HOME}/.pspman" "${HOME}/.pspman/src/pspman"
    source ~/.bashrc
}

function del_pspman() {
    oldpwd="${PWD}"
    cd "${HOME}" || exit
    count=10
    until ! pip uninstall -y pspman >>/dev/null; do
        if [[ $count -lt 1 ]]; then
            exit 1
        fi
        count=$(( count - 1 ))
        echo "Tried uninstalling pspman, aborting..."
    done
    count=
    cd "$oldpwd"  || exit
}

function uninstall() {
    python3 ./_install.py douninstall
    del_pspman
}

case "$1" in
    install)
        install $@
        ;;
    uninstall)
        uninstall
        ;;
    *)
        echo ""
        echo "usage: bash install.sh install"
        echo "       bash install.sh uninstall"
        echo ""
esac
