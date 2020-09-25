#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This le is part of pspman.
#
# pspman is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pspman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pspman.  If not, see <https://www.gnu.org/licenses/>.
#
'''
Personal Simple Python-based package manager that clones git
'''


from os import getcwd, chdir, makedirs
from shutil import rmtree
from os.path import isdir, isfile
from sys import exit as sysexit
from subprocess import Popen, PIPE
from pathlib import Path
from re import compile as recompile
from .classes import InstallEnv
from .input_output import print_info, cli


def git_pulls(env: InstallEnv) -> list:
    '''
    Pull git projects
    '''
    fails = 0
    pull_paths = []
    for git_path in env.git_project_paths:
        chdir(git_path)
        call = Popen(["git", "pull"],
                     stderr=PIPE, stdout=PIPE, text=True)
        stdout, stderr = call.communicate()
        if "Already up to date" not in stdout:
            print_info()
            print_info(f"Updating {git_path}", 1)
            if any(m in stdout for m in ("+", "-")):
                pull_paths.append(git_path)
            else:
                fails += 1
                print_info(f"Failed in {git_path}", 3)
    chdir(env.base_dir)
    for update in pull_paths:
        print_info(f"Updated {update}", 1)
    print_info("", 0)
    if fails:
        print_info(f"{fails} project updates failed", 1)
    return pull_paths


def specific_unknown(_) -> int:
    '''
    Unknown protocol for installation
    '''
    return 0


def specific_make(env: InstallEnv) -> int:
    '''
    install specific make
    return: failure: 1; success: 0
    '''
    if Path("./configure").exists():
        call = Popen(["./configure", "--prefix", env.prefix],
                     stdout=PIPE, stderr=PIPE, text=True)
        stdout, stderr = call.communicate()
        if stderr:
            return 1
    if Path("./Makefile").exists():
        call = Popen(["make"],
                     stdout=PIPE, stderr=PIPE, text=True)
        stdout, stderr = call.communicate()
        if stderr:
            return 1
        call = Popen(["make", "install"],
                     stdout=PIPE, stderr=PIPE)
        stdout, stderr = call.communicate()
        if stderr:
            return 1
    return 0


def specific_pip(_) -> int:
    '''
    specific python setup
    return: failure: 1; success: 0
    '''
    call = Popen(["pip", "install", "--user", "-U", "."],
                 stdout=PIPE, stderr=PIPE, text=True)
    stdout, stderr = call.communicate()
    if stderr:
        return 1
    return 0


def specific_meson(env: InstallEnv) -> int:
    ''' specific meson/ninja return: failure: 1; success: 0
    '''
    update_dir = "./build/update"
    makedirs(f'{getcwd}/subprojects', exist_ok=True)
    call = Popen(["gitman", "-c", f"{getcwd()}/subprojects"],
                 stdout=PIPE, stderr=PIPE, text=True)
    stdout, stderr = call.communicate()
    makedirs(update_dir, exist_ok=True)
    call = Popen(["meson", "--wipe", "--buildtype=release", "--prefix",
                 env.prefix, "-Db_lto=true", update_dir],
                 stdout=PIPE, stderr=PIPE, text=True)
    stdout, stderr = call.communicate()
    if stderr:
        call = Popen(["meson", "--buildtype=release", "--prefix",
                     env.prefix, "-Db_lto=true", update_dir],
                     stdout=PIPE, stderr=PIPE, text=True)
        stdout, stderr = call.communicate()
        if stderr:
            return 1
    chdir(update_dir)
    call = Popen(["ninja"], stderr=PIPE, stdout=PIPE, text=True)
    stdout, stderr = call.communicate()
    if stderr:
        return 1
    call = Popen(["ninja", "install"], stderr=PIPE, stdout=PIPE, text=True)
    stdout, stderr = call.communicate()
    if stderr:
        return 1
    return 0


def install_wrap(env: InstallEnv, projects_list: list,
                 install_type: int) -> None:
    '''
    install_type: integer indicating installs:
    0: unknown
    1: make
    2: pip
    3: meson
    projects_list: list of projects to be installed

    parent definition object for all kinds of install
    '''
    inst_protocol = [
        "Unknown",
        "./configure -> make -> make install",
        "pip install --user -U .",
        "meson/ninja",
    ]
    print_info("", 0)
    print_info("Looks like the method of installation is", 1)
    print_info(inst_protocol[install_type], 0)
    print_info("for the following projects", 0)
    print_info("", 0)
    for proj in projects_list:
        print_info(proj, 5)
        chdir(proj)
        # TODO: UPDATE Flag if already present
        print_info(f"cd {getcwd()}", 1)
        err = [specific_unknown, specific_make,
               specific_pip, specific_meson][install_type](env)
        if err:
            print_info("Failed", 4)
            continue
    chdir(env.base_dir)
    print_info("", 0)


def auto_install(git_paths: list, env: InstallEnv) -> None:
    unknown_installs = []
    make_projects = []
    meson_projects = []
    pip_projects = []
    protocols = (
        unknown_installs,
        make_projects,
        pip_projects,
        meson_projects,
    )
    for git_path in git_paths:
        if git_path.joinpath("Makefile").exists():
            make_projects.append(git_path)
        elif git_path.joinpath('configure').exists():
            make_projects.append(git_path)
        elif git_path.joinpath('setup.py').exists():
            pip_projects.append(git_path)
        elif git_path.joinpath('meson.build').exists():
            meson_projects.append(git_path)
        else:
            unknown_installs.append(git_path)
    for index, proj_protocol in enumerate(reversed(protocols)):
        if proj_protocol:
            install_wrap(env=env, projects_list=proj_protocol,
                         install_type=len(protocols) - index - 1)


def new_install(env: InstallEnv) -> None:
    makedirs(env.clonedir, exist_ok=True)
    node_pat = recompile("(.*?)/")
    clone_paths_list = []
    for url in env.pkg_install:
        if url[-1] != "/":
            url += "/"
        package = node_pat.findall(url)[-1].replace(".git", "").split(":")[-1]
        package_dir = Path.joinpath(env.clonedir, package)
        if isdir(package_dir):
            print_info(f"{package} appears to be installed already", 3)
        elif isfile(package_dir):
            print_info(f"A file named '{package_dir}' already exists", 3)
            package_dir = package_dir.joinpath(".d")
            if package_dir.exists():
                print_info("", 0)
                print_info(f"{package_dir} also exists,", 3)
                print_info("This is too much to handle...", 4)
                continue
            print_info(f"Calling this project '{package_dir}'", 3)
            print_info(f"Installing in {package_dir}", 1)
            chdir(env.clonedir)
            makedirs(package_dir, exist_ok=False)
            call = Popen(["git", "clone", url, str(package_dir)],
                         stdout=PIPE, stderr=PIPE, text=True)
            stdout, stderr = call.communicate()
            clone_paths_list.append(package_dir)
            if stderr:
                return False
    auto_install(clone_paths_list, env)


def del_proj(env: InstallEnv) -> None:
    for package in env.pkg_delete:
        pkg_path = Path.joinpath(env.clonedir, package)
        if not isdir(pkg_path):
            print_info(f"Couldn't find {package} in {env.clonedir}", 3)
            print_info("Ignoring...", 0)
            continue
        chdir(pkg_path)
        call = Popen(["git", "remote", "-v"],
                     stdout=PIPE, stderr=PIPE, text=True)
        stdout, stderr = call.communicate()
        if stderr:
            return False
        fetch_source = recompile(r"^.*fetch.*").findall(
            stdout)[0].split(" ")[-2].split("\t")[-1]
        print_info(f"Deleting {pkg_path}", 1)
        print_info("I can't guess which files were installed.", 1)
        print_info("So, leaving those scars behind...", 0)
        print_info("This project may be added again from the following path",
                   0)
        print_info(f"{fetch_source}", 0)
        chdir(env.clonedir)
        rmtree(Path.joinpath(env.clonedir, package))


def main() -> None:
    args = cli()
    pkg_grp = InstallEnv(
        clonedir=args.clone_dir,
        prefix=args.prefix,
        only_pull=args.only_pull,
        force_root=args.force_root,
        pkg_install=args.pkg_install or "",
        pkg_delete=args.pkg_delete or "",
    )
    del_proj(env=pkg_grp)
    pkg_grp.find_gits()
    updates = git_pulls(env=pkg_grp)
    auto_install(updates, pkg_grp)
    new_install(pkg_grp)
    chdir(pkg_grp.base_dir)
    print_info("done.", 1)
    sysexit(0)


if __name__ == "__main__":
    main()
