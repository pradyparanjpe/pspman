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
Personal Simple Python-based package manager that clones git
'''


from os import getcwd, chdir, makedirs, environ
from os.path import isdir, isfile
from shutil import rmtree
from sys import exit as sysexit
from subprocess import Popen, PIPE
from pathlib import Path
from re import compile as recompile
from psprint import PRINT as print
from .classes import InstallEnv
from .input_output import cli


def git_pulls(env: InstallEnv) -> list:
    '''
    Pull git projects
    '''
    pull_paths = []
    fails = 0
    if env.opt_flags['stale']:
        print("But not trying to update them.", pref=1, pad=True)
        return pull_paths
    for git_path in env.git_project_paths:
        chdir(git_path)
        call = Popen(["git", "pull", "--recurse-submodules"],
                     stderr=PIPE, stdout=PIPE, text=True)
        stdout, _ = call.communicate()
        if "Already up to date" not in stdout:
            print(f"Updating {git_path}", pref=1, pad=True)
            if any(m in stdout for m in ("+", "-")):
                pull_paths.append(git_path)
            else:
                fails += 1
                print(f"Failed in {git_path}", pref=4, pad=True)
    print()
    chdir(env.base_dir)
    for update in pull_paths:
        print(f"Updated {update}", pref=3, pad=True)
    print("", pref=0, pad=True)
    if fails:
        print(f"{fails} project updates failed", pref=1, pad=True)
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
        _, stderr = call.communicate()
        if stderr:
            return 1
    if Path("./Makefile").exists():
        call = Popen(["make"],
                     stdout=PIPE, stderr=PIPE, text=True)
        _, stderr = call.communicate()
        if stderr:
            return 1
        call = Popen(["make", "install"],
                     stdout=PIPE, stderr=PIPE)
        _, stderr = call.communicate()
        if stderr:
            return 1
    return 0


def specific_go(env:InstallEnv) -> int:
    '''
    specific go setup
    return: failure:1; success:0
    '''
    myenv = environ.copy()
    myenv['GOBIN'] = f"{env.prefix}/bin"
    call = Popen(["go", "install"], env=myenv,
                 stdout=PIPE, stderr=PIPE, text=True)
    _, stderr = call.communicate()
    if stderr:
        return 1
    return 0


def specific_pip(_) -> int:
    '''
    specific python setup
    return: failure: 1; success: 0
    '''
    if Path("./requirements.txt").exists():
        call = Popen(["python", "-m", "pip", 'install', '-U',
                      '--user', "-r", "./requirements.txt"],
                     stdout=PIPE, stderr=PIPE, text=True)
        _, stderr = call.communicate()
        if stderr:
            return 1
    call = Popen(["python", "-m", "pip", "install", "--user", "-U", "."],
                 stdout=PIPE, stderr=PIPE, text=True)
    _, stderr = call.communicate()
    if stderr:
        return 1
    return 0


def specific_meson(env: InstallEnv) -> int:
    ''' specific meson/ninja return: failure: 1; success: 0
    '''
    update_dir = "./build/update"
    makedirs(f'{getcwd()}/subprojects', exist_ok=True)
    call = Popen(["pspman", "-c", f"{getcwd()}/subprojects"],
                 stdout=PIPE, stderr=PIPE, text=True)
    _, stderr = call.communicate()
    makedirs(update_dir, exist_ok=True)
    call = Popen(["meson", "--wipe", "--buildtype=release", "--prefix",
                  env.prefix, "-Db_lto=true", update_dir],
                 stdout=PIPE, stderr=PIPE, text=True)
    _, stderr = call.communicate()
    if stderr:
        call = Popen(["meson", "--buildtype=release", "--prefix",
                      env.prefix, "-Db_lto=true", update_dir],
                     stdout=PIPE, stderr=PIPE, text=True)
        _, stderr = call.communicate()
        if stderr:
            return 1
    chdir(update_dir)
    call = Popen(["ninja"], stderr=PIPE, stdout=PIPE, text=True)
    _, stderr = call.communicate()
    if stderr:
        return 1
    call = Popen(["ninja", "install"], stderr=PIPE, stdout=PIPE, text=True)
    _, stderr = call.communicate()
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
        "go install"
    ]
    print("", pref=0, pad=True)
    print("Looks like the method of installation is", pref=1, pad=True)
    print(inst_protocol[install_type], pref=0, pad=True)
    print("for the following projects", pref=0, pad=True)
    print("", pref=0, pad=True)
    for proj in projects_list:
        print(proj, pref=3, pad=True)
        chdir(proj)
        print(f"cd {getcwd()}", pref=1, pad=True)
        err = [specific_unknown, specific_make,
               specific_pip, specific_meson, specific_go][install_type](env)
        if err:
            print("Failed", pref=4, pad=True)
            continue
    chdir(env.base_dir)
    print("", pref=0, pad=True)


def auto_install(git_paths: list, env: InstallEnv) -> None:
    '''
    automated clone and install attempt
    '''
    if env.opt_flags['only_pull']:
        return
    unknown_installs = []
    make_projects = []
    meson_projects = []
    go_projects = []
    pip_projects = []
    protocols = (
        unknown_installs,
        make_projects,
        pip_projects,
        meson_projects,
        go_projects,
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
        elif git_path.joinpath('main.go').exists():
            go_projects.append(git_path)
        else:
            unknown_installs.append(git_path)
    for index, proj_protocol in enumerate(reversed(protocols)):
        if proj_protocol:
            install_wrap(env=env, projects_list=proj_protocol,
                         install_type=len(protocols) - index - 1)
    return


def new_install(env: InstallEnv) -> None:
    '''
    install given project
    '''
    makedirs(env.clonedir, exist_ok=True)
    node_pat = recompile("(.*?)/")
    clone_paths_list = []
    for url in env.pkg_install:
        if url[-1] != "/":
            url += "/"
        package = node_pat.findall(url)[-1].replace(".git", "").split(":")[-1]
        package_dir = Path.joinpath(env.clonedir, package)
        if isdir(package_dir):
            print(f"{package} appears to be installed already", pref=3, pad=True)
            return
        if isfile(package_dir):
            print(f"A file named '{package_dir}' already exists", pref=3, pad=True)
            package_dir = package_dir.joinpath(".d")
            if package_dir.exists():
                print("", pref=0, pad=True)
                print(f"{package_dir} also exists,", pref=3, pad=True)
                print("This is too much to handle...", pref=4, pad=True)
                continue
            print(f"Calling this project '{package_dir}'", pref=3, pad=True)
            print(f"Installing in {package_dir}", pref=1, pad=True)
        chdir(env.clonedir)
        makedirs(package_dir, exist_ok=False)
        call = Popen(["git", "clone", '--recursive', url, str(package_dir)],
                     stdout=PIPE, stderr=PIPE, text=True)
        _, _ = call.communicate()
        clone_paths_list.append(package_dir)
    auto_install(clone_paths_list, env)


def del_proj(env: InstallEnv) -> None:
    '''
    delete given project
    '''
    for package in env.pkg_delete:
        pkg_path = Path.joinpath(env.clonedir, package)
        if not isdir(pkg_path):
            print(f"Couldn't find {package} in {env.clonedir}", pref=3, pad=True)
            print("Ignoring...", pref=0, pad=True)
            continue
        chdir(pkg_path)
        call = Popen(["git", "remote", "-v"],
                     stdout=PIPE, stderr=PIPE, text=True)
        stdout, stderr = call.communicate()
        if stderr:
            return
        fetch_source = recompile(r"^.*fetch.*").findall(
            stdout)[0].split(" ")[-2].split("\t")[-1]
        print(f"Deleting {pkg_path}", pref=1, pad=True)
        print("I can't guess which files were installed.", pref=1, pad=True)
        print("So, leaving those scars behind...", pref=0, pad=True)
        print("This project may be added again from the following path",
              pref=0)
        print(f"{fetch_source}", pref=0, pad=True)
        chdir(env.clonedir)
        rmtree(Path.joinpath(env.clonedir, package))


def main() -> None:
    '''
    main subroutine
    '''
    args = cli()
    pkg_grp = InstallEnv(
        clonedir=args.clone_dir,
        prefix=args.prefix,
        pkg_install=args.pkg_install or "",
        pkg_delete=args.pkg_delete or "",
        stale=args.stale or False,
        force_root=args.force_root,
        only_pull=args.only_pull,
    )
    del_proj(env=pkg_grp)
    pkg_grp.find_gits()
    updates = git_pulls(env=pkg_grp)
    auto_install(updates, pkg_grp)
    new_install(env=pkg_grp)
    chdir(pkg_grp.base_dir)
    print("done.", pref=1, pad=True)
    sysexit(0)


if __name__ == "__main__":
    main()
