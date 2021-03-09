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


function add_to_path() {
    dir_struct=( "bin" "share" "lib" "lib64" "include" "etc" "tmp" "src" )
    if [[ ! $PATH =~ "${HOME}/.local/bin" ]]; then
        echo "export PATH=\"\${PATH}:\${HOME}/.local/bin\"" >> "${HOME}/.bashrc"
    fi
    if [[ ! $PATH =~ "${HOME}/.pspman/bin" ]]; then
        echo "export PATH=\"\${PATH}:\${HOME}/.pspman/bin\"" >> "${HOME}/.bashrc"
    fi
    source "${HOME}/.bashrc"
    mkdir -p "${HOME}/.pspman"
    for workdir in dir_struct; do
        mkdir -p "${HOME}/.pspman/${workdir}"
    done
}

function get_pip() {
    if ! test $(command -v pip); then
        wget "https://bootstrap.pypa.io/get-pip.py"
        python3 "get-pip.py" --user
        rm get-pip.py
    fi
    echo "Updating pip"
    python3 -m "pip" install --user -U pip
}

function get_pspman() {
    echo "installing pspman"
    python3 -m pip install --user -U pspman
}

function install() {
    add_to_path
    if ! test $(command -v python); then
        echo "Please install python3 first"
        exit 1
    fi
    get_pip
    get_pspman
    echo "Updating Pspman"
    python3 -m 'pspman' -i pspman
}

function restore_path() {
    sed -i -e "s|^export PATH=\"\${PATH}:\${HOME}/.pspman/bin\"||" \
        "${HOME}/.bashrc"
}

function del_pspman() {
    pip uninstall -y pspman
}

function uninstall() {
    restore_path
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
