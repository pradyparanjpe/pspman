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


if [[ ! -f "./install.py" ]]; then
    wget https://github.com/pradyparanjpe/pspman/blob/master/install.py
fi


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
    if ! test "$(command -v python)"; then
        echo "Please install python3 first"
        exit 1
    fi
    get_pip
    python3 ./install.py install
    echo "Updating Pspman"
    python3 -m pspman -s -i https://github.com/pradyparanjpe/pspman.git
    python3 -m pip install --prefix "${HOME}/.pspman" "${HOME}/.pspman/src/pspman"
    source ~/.bashrc
}

function del_pspman() {
    oldpwd="${PWD}"
    cd "${HOME}" || exit
    pip uninstall -y pspman
    cd "$oldpwd"  || exit
}

function uninstall() {
    python3 ./install.py uninstall
    del_pspman
}

case "$1" in
    install)
        install
        ;;
    uninstall)
        uninstall
        ;;
    *)
        echo ""
        echo "usage: bash ./install.sh install"
        echo "       bash ./install.sh uninstall"
        echo ""
esac
