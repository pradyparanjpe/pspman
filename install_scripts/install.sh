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


pspbase="${HOME}/.pspman"
inst_temp_dir="${pspbase}/pspman_install_temp"


function already_installed() {
    if test "command -v pspman >> /dev/null"; then
        echo -e "
        \033[0;91mPSPMAN is already installed:\033[0m
        $( pspman version ) .


        \033[0;94mIf you wish to install afresh...\033[0m

        1) Uninstall pspman using \033[1;97;40mpip\033[0m: type without '# ':

        \033[0;97;40m# until command -v pspman >/dev/null; \
do pip uninstall -y pspman >/dev/null; done\033[0m

        2) Remove pspman clone from its standard location: type without '# ':

        \033[0;97;40m# rm -rf \"${pspbase}/src/pspman\"\033[0m

        ... and initiate installation again:

        I am aborting for now without making any changes.
"
        exit 1
    fi
}


function create_temp_install() {
    mkdir -p "${inst_temp_dir}"
    cd "${inst_temp_dir}"
}


function inst_fail() {
    echo "Failed installing $1"
    echo "aborting..."
    cd "{$oldpwd}"
    exit 1
}


function get_tar() {
    echo "TAR archive not found"
    echo "Install all dependencies and then run this script"
    exit 1
}


function get_wget() {
    echo "wget not found"
    echo "Install all dependencies and then run this script"
    exit 1
}


function get_gcc() {
    echo "CC not found install c compiler globally"
    exit 1
}


function get_make() {
    make_ver="4.3"
    make_url="ftp://ftp.gnu.org/gnu/make/\
make-${make_ver}.tar.gz"
    wget "${make_url}"
    tar -xzf "make-${make_ver}.tar.gz"
    cd "make-${make_ver}"
    ./configure --prefix="${pspbase}"
    ./install.sh
    cd "${inst_temp_dir}"
}


function get_python3() {
    python_ver="3.9.2"
    python_url="https://www.python.org/ftp/python/3.9.2/\
Python-${python_ver}.tgz"
    wget "${python_url}"
    tar -xzf "Python-${python_ver}.tgz"
    cd "Python-${python_ver}"
    ./configure --prefix="${pspbase}"
    make
    make install
    cd "${inst_temp_dir}"
}


function get_pip() {
    wget "https://bootstrap.pypa.io/get-pip.py"
    python3 "get-pip.py" --prefix="${pspbase}"
    python3 -m "pip" install --user -U pip setuptools wheel
}


function get_git() {
    git_ver="2.30.2"
    git_url="https://mirrors.edge.kernel.org/pub/software/scm/git/\
git-${git_ver}.tar.gz"
    wget "${git_url}"
    tar -xzf "git-${git_ver}.tar.gz"
    cd "git-${git_ver}"
    ./configure --prefix="${pspbase}"
    make
    make install
    cd "${inst_temp_dir}"
}


function get_go() {
    go_ver="1.16.2"
    go_url="https://golang.org/dl/\
go${go_ver}.linux-amd64.tar.gz"
    wget "${go_url}"
    tar -xzf "go${go_ver}.linux-amd64.tar.gz"
    for binfile in ./go/bin/*; do
        cp "$binfile" "${pspbase}/bin/."
    done
}


function get_meson() {
    pip install --prefix="${pspbase}" -U meson
}


function check_dep() {
    dep="$1"
    if ! test "$(command -v $dep)"; then
        echo "${dep} is not installed"
        echo "1. (Recommended) install ${dep} and run this script"
        echo "2. (Discouraged) try installing ${dep} locally"
        echo -e "[1/2]:\t"
        read choice
        if [[ "${choice}" != "2" ]]; then
            echo "GOOD! Aborting installation."
            exit 0
        fi
        echo "Trying a local install of ${dep} this is not a good idea!"
        get_${dep}
    fi
}

function install() {
    already_installed $@

    oldpwd="${PWD}"

    create_temp_install

    export PATH="${pspbase}/bin:${PATH}"
    python_ver="$(python3 --version |cut -d "." -f1,2 |sed 's/ //' |sed 's/P/p/')"
    export PYTHONPATH="${pspbase}/lib/{}/site-packages:${PYTHONPATH}"

    for dep in "tar" "make" "python3" "pip" "git" "go" "meson"; do
        check_dep "${dep}"
    done

    if [[ ! -f "_install.py" ]]; then
        wget "https://raw.githubusercontent.com/pradyparanjpe/\
pspman/master/install_scripts/_install.py" || inst_fail "pspman (download)"
    fi


    python3 ./_install.py doinstall || \
        inst_fail pspman via bootstrap

    python3 -m pip install --prefix="${pspbase}" -U pspman || \
        inst_fail pspman# Temporary

    python3 -m pspman -s -i https://github.com/pradyparanjpe/pspman.git \
        || inst_fail pspman

    python3 -m pip install --prefix "${pspbase}" -U "${pspbase}/src/pspman"

    pspman version || inst_fail "pspman"

    cd "${oldpwd}"

    echo -e "Installation over"
    echo -e "Start a new shell (terminal) or run without '# ':"
    echo -e "\033[1;97;40msource ${HOME}/bashrc\033[0m"
}

function del_pspman() {
    oldpwd="${PWD}"
    cd "${HOME}" || exit
    count=10
    until command -v pspman >/dev/null; do
        pip uninstall -y pspman >>/dev/null
        if [[ $count -lt 1 ]]; then
            exit 1
        fi
        count=$(( count - 1 ))
        echo "Tried uninstalling pspman, failed ${count} times"
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
