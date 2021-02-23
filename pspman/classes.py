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
Environment Classes

'''


import os
import sys
import typing
import time
import pathlib
import shutil
import re
from . import common, print


def timeout(wait: int = 10) -> None:
    '''
    Print a count-down time that waits for the process to get killed

    Args:
        wait: wait for seconds

    '''
    for time_out in range(wait):
        time.sleep(1)
        print(f"{wait - time_out:2.0f} seconds...", end="",
              flush=True, pad=False)
        print("\b" * 13, end="",
              flush=True, pad=True)
    print(f"{wait:2.0f} seconds...")


class TagError(Exception):
    '''
    Error in tagging a git for type of modification (pull, install, etc)

    Args:
        old_tag: existing tag
        operate: operation intended

    '''

    def __init__(self, old_tag: int, operate: str) -> None:
        super().__init__(f'''
        Tag '{old_tag}' can't be operated by '{operate}'
        ''')


class DirDB():
    '''
    Database holding information about clonedir
    [Future feature]

    Args:
        clonedir: Directory in which gits are cloned and maintained
        prefix:  Directory in which "bin", "share", "lib" are stored

    '''

    def __init__(self, **kwargs) -> None:
        for key, val in kwargs.items():
            setattr(self, key, val)
        self.install_types = []


class ActionTag():
    '''
    Coded information about update method.
    For Bytecode B, B < 8, F - B = Failure Code

    Values:
        0x00: Do nothing
        0x01: List
        0x02: Pull
        0x04: Try install
        0x0B: Install Failed
        0x0D: Pull Failed
        0x0E: List Failed
        0x10: Make
        0x20: Pip
        0x30: Meson/Ninja
        0x40: Go
        0xB0: Go failed
        0xC0: Meson/Ninja Failed
        0xD0: Pip failed
        0xE0: Make Failed
        0xFF: Failed at everything
    '''

    def __init__(self, x: int = 0) -> None:
        self.tag = x

    def show_list(self) -> None:
        '''
        flag show in list
        '''
        self.tag |= 0x01

    def pull(self) -> None:
        '''
        flag pull = True
        '''
        self.tag |= 0x02

    def try_install(self) -> None:
        '''
        flag install try
        '''
        self.tag |= 0x04

    def make(self) -> None:
        '''
        flag install for make method

        Raises:
            TagError: already tagged

        '''
        if (0x0 < self.tag//0x10 < 0x5):
            if not self.tag & 0x10:
                # already tagged
                raise TagError(self.tag, 'make')
        else:
            self.tag |= 0x10

    def pip(self) -> None:
        '''
        flag install for pip

        Raises:
            TagError: already tagged

        '''
        if (0x0 < self.tag//0x10 < 0x5):
            if not self.tag & 0x20:
                # already tagged
                print(self.tag, mark='bug')
                raise TagError(self.tag, 'pip')
        else:
            self.tag |= 0x20

    def meson(self) -> None:
        '''
        flag install for meson

        Raises:
            TagError: already tagged

        '''
        if (0x0 < self.tag//0x10 < 0x5):
            if not self.tag & 0x30:
                # already tagged
                raise TagError(self.tag, 'meson')
        else:
            self.tag |= 0x30

    def goin(self) -> None:
        '''
        flag install for meson

        Raises:
            TagError: already tagged

        '''
        if (0x0 < self.tag//0x10 < 0x5):
            if not self.tag & 0x40:
                # already tagged
                raise TagError(self.tag, 'go')
        else:
            self.tag |= 0x40

    def err(self) -> None:
        '''
        Invert flags due to error

        '''
        self.tag = 0xff - self.tag


class InstallEnv():
    '''
    Installation Environment

    Args:
        clonedir: Directory in which gits are cloned and maintained
        prefix: Directory in which "bin", "share", "lib" are stored
        pkg_install: List of new packages to install
        pkg_delete: List of new packages to delete
        force_root: Force installation as ROOT (Administrator) flag
        only_pull: do not try to install pulled gits flag
        stale: do not pull gits flag

    Attributes:
        basedir: current working directory to return to
        clonedir: Path of clonedir
        prefix: Path to prefix
        pkg_install: list of urls for new packages to install
        pkg_delete: list of dir-names of packages to delete
        opt_flags: flags opted
        git_project_paths: {path of project: ``update_byte``}
        db: DirDB [Future]

    '''

    def __init__(self, clonedir: str, prefix: str, pkg_install: list = None,
                 pkg_delete: list = None, only_pull: bool = False,
                 force_root: bool = False, stale: bool = None) -> None:
        # options
        self.base_dir = os.getcwd()
        self.clonedir = pathlib.Path(clonedir).resolve()
        self.prefix = pathlib.Path(prefix).resolve()
        self.pkg_install = pkg_install or []
        self.pkg_delete = pkg_delete or []
        self.opt_flags = {"only_pull": only_pull,
                          "force_root": force_root,
                          "stale": stale}

        # inits
        os.makedirs(self.clonedir, exist_ok=True)
        os.makedirs(self.prefix, exist_ok=True)
        self.git_project_paths: typing.Dict[pathlib.Path, ActionTag] = {}
        self.permission_check()

    def find_gits(self) -> None:
        '''
        Locate git projects in current ``clone_db``
        '''
        for leaf in os.listdir(self.clonedir):
            if os.path.isdir(pathlib.Path.joinpath(self.clonedir, leaf)):
                if os.path.isdir(
                        pathlib.Path.joinpath(self.clonedir, leaf, ".git")
                ):
                    self.git_project_paths[
                        pathlib.Path.joinpath(self.clonedir, leaf)
                    ] = ActionTag(0x02 * (not self.opt_flags['stale']))
        print(f"{len(self.git_project_paths)} project(s)",
              f"found in {str(self.clonedir)}", mark=1, sep=" ")

    def permission_check(self) -> None:
        '''
        Check permissions in the given context
        '''
        # Am I root?
        if os.environ["USER"].lower() == "root":
            print("I hate dictators", mark=3)
            if not self.opt_flags['force_root']:
                print("Bye", mark=0)
                sys.exit(2)
            print("I can only hope you know what you are doing...",
                  mark=3)
            print("Here is a chance to kill me in", mark=2)
            timeout(10)
            print("", mark=0)
            print("¯\\_(ツ)_/¯ Your decision ¯\\_(ツ)_/¯", mark=3)
            print("", mark=0)
            print("[INFO] Proceeding...", mark=1)
        else:
            # Is installation directory read/writable
            parentdir = pathlib.Path(self.clonedir)
            while not os.path.isdir(parentdir):
                parentdir = pathlib.Path(parentdir).parent
            self.perm_pass(parentdir)
            self.perm_pass(self.prefix)

    @staticmethod
    def perm_pass(permdir: str) -> None:
        '''
        Args:
            permdir: directory whose permissions are to be checked

        Returns:
            True if all rwx permissions are granted

        '''
        stdout = common.process_comm("stat", "-L", "-c", "%U %G %a", permdir,
                                     fail_handle='report')
        if stdout is None:
            print("aborting...", mark=4)
            sys.exit(1)
        owner, group, octperm = stdout.replace("\n", "").split(" ")
        if (octperm[-1] == "7") != 0:
            # everyone has access
            return True
        if (octperm[-2] == "7") != 0:
            # some group has permissions
            stdout = common.process_comm(
                "groups", os.environ["USER"], fail_handle='report'
            )
            if stdout is None:
                # error
                print("aborting...", mark=4)
                sys.exit(1)
            user_groups = stdout.split(" ")
            for u_grp in user_groups:
                if u_grp == group:
                    return True
        if (octperm[-3] == "7") != 0:
            # owner has permissions
            if os.environ["USER"] == owner:
                return True
        print("We do not have sufficient permissions", mark=4)
        print("Try another location", mark=2)
        print("Bye", mark=0)
        sys.exit(1)
        return False

    def install_make(self) -> int:
        '''
        Try to install by calling ./configure -> make -> make install

        Args:
            self: Install with this environment

        '''
        print()
        print(f"configure --prefix={str(self.prefix)} -> make -> make install",
              mark=1)
        print()
        for package, action in self.git_project_paths.items():
            if not action.tag & 0x10:
                # not a meson installation
                continue
            print(f"{os.path.basename(package)}", mark='list')
            configure = package.joinpath('configure')
            makefile = package.joinpath('Makefile')
            if configure.exists():
                conf_out = common.process_comm(
                    f'{str(configure)}', "--prefix", self.prefix,
                    fail_handle='report'
                )
                if conf_out is None:
                    self.git_project_paths[package].err()
            if pathlib.Path("./Makefile").exists():
                make_out = common.process_comm(
                    'make', '-C', f'{str(makefile)}', fail_handle='report'
                )
                if make_out is None:
                    self.git_project_paths[package].err()
                make_install_out = common.process_comm(
                    'make', '-C', f'{str(makefile)}', 'install',
                    fail_handle='report'
                )
                if make_install_out is None:
                    self.git_project_paths[package].err()


    def install_go(self) -> int:
        '''
        Install repository by ``go install``

        Args:
            self: Install with this environment

        '''
        print()
        print(f"go install", mark=1)
        print()
        for package, action in self.git_project_paths.items():
            if action.tag & 0x40 != 0x40:
                # not a meson installation
                continue
            print(f"{os.path.basename(package)}", mark='list')
            myself = os.environ.copy()
            myself['GOBIN'] = str(self.prefix.resolve('bin'))
            go_in = common.process_comm(
                "go", "install", "-i", '-pkgdir', f'{str(package)}',
                fail_handle='report'
            )
            if go_in is None:
                self.git_project_paths[package].err()


    def install_pip(self) -> int:
        '''
        Install repository using ``pip``

        Args:
            self: Install with this environment

        '''
        print()
        print(f"pip install", mark=1)
        print()
        for package, action in self.git_project_paths.items():
            if not action.tag & 0x20:
                # not a meson installation
                continue
            print(f"{os.path.basename(package)}", mark='list')
            if pathlib.Path("./requirements.txt").exists():
                pip_req = common.process_comm(
                    "python", "-m", "pip", 'install', '-U', '--user', "-r",
                    f"{str(package).joinpath('requirements.txt')}",
                    fail_handle='report')
                if pip_req:
                    self.git_project_paths[package].err()
            pip_in = common.process_comm(
                "python", "-m", "pip", "install", "--user", "-U",
                f"{str(package)}", fail_handle='report'
            )
            if pip_in is None:
                self.git_project_paths[package].err()


    def install_meson(self) -> int:
        '''
        Install repository by building with ninja/json

        Args:
            self: Install with this environment

        '''
        print()
        print(f"meson/ninja install", mark=1)
        print()
        for package, action in self.git_project_paths.items():
            if not action.tag & 0x30:
                # not a meson installation
                continue
            print(f"{os.path.basename(package)}", mark='list')
            update_dir = package.joinpath("build", "update")
            subproject_dir = package.joinpath('subprojects')
            os.makedirs(subproject_dir, exist_ok=True)
            _ = common.process_comm("pspman", "-c", str(subproject_dir),
                                    fail_handle='report')
            os.makedirs(update_dir, exist_ok=True)
            build = common.process_comm(
                "meson", "--wipe", "--buildtype=release", "--prefix",
                self.prefix, "-Db_lto=true", update_dir, fail_handle='report'
            )
            if build is None:
                build = common.process_comm(
                    "meson", "--buildtype=release", "--prefix", self.prefix,
                    "-Db_lto=true", update_dir, fail_handle='report'
                )

                if build is None:
                    self.git_project_paths[package].err()
            os.chdir(update_dir)
            ninja = common.process_comm("ninja", fail_handle='report')
            if ninja is None:
                self.git_project_paths[package].err()
            ninja_in = common.process_comm('ninja', 'install',
                                           fail_handle='report')
            if ninja_in is None:
                self.git_project_paths[package].err()


    def auto_install(self) -> None:
        '''
        Automated clone and install attempt

        Args:
            git_paths: path of cloned git repositories
            self: Install with this environment

        '''
        if self.opt_flags['only_pull']:
            return
        for git_path, action in self.git_project_paths.items():
            if not action.tag & 0x04:
                continue
            if git_path.joinpath("Makefile").exists():
                self.git_project_paths[git_path].make()
            elif git_path.joinpath('configure').exists():
                self.git_project_paths[git_path].make()
            elif git_path.joinpath('setup.cfg').exists():
                self.git_project_paths[git_path].pip()
            elif git_path.joinpath('setup.py').exists():
                self.git_project_paths[git_path].pip()
            elif git_path.joinpath('meson.build').exists():
                self.git_project_paths[git_path].meson()
            elif git_path.joinpath('main.go').exists():
                self.git_project_paths[git_path].goin()
            else:
                pass
        self.install_go()
        self.install_make()
        self.install_meson()
        self.install_pip()
        return


    def new_install(self) -> None:
        '''
        Install given project

        Args:
            self: Install with this environment

        '''
        os.makedirs(self.clonedir, exist_ok=True)
        node_pat = re.compile("(.*?)/")
        for url in self.pkg_install:
            if url[-1] != "/":
                url += "/"
            package = node_pat.findall(url)[-1]\
                              .replace(".git", "").split(":")[-1]
            package_dir = pathlib.Path.joinpath(self.clonedir, package)\
                                      .resolve()
            if os.path.isdir(package_dir):
                print(f"{package} appears to be installed already",
                      mark=3)
                return
            if os.path.isfile(package_dir):
                print(f"A file named '{package_dir}' already exists",
                      mark=3)
                package_dir = package_dir.joinpath(".d")
                if package_dir.exists():
                    print("", mark=0)
                    print(f"{package_dir} also exists,", mark=3)
                    print("This is too much to handle...", mark=4)
                    continue
                print(f"Calling this project '{package_dir}'", mark=3)
                print(f"Installing in {package_dir}", mark=1)
            os.makedirs(package_dir, exist_ok=False)
            _ = common.process_comm(
                'git', "-C", f"{str(self.clonedir)}",
                'clone', url, fail_handle='report'
            )
            self.git_project_paths[package_dir] = ActionTag(0x04)


    def del_proj(self) -> None:
        '''
        Delete given project

        Args:
            self: Install with this environment
        '''
        for package in self.pkg_delete:
            pkg_path = pathlib.Path.joinpath(self.clonedir, package)
            if not os.path.isdir(pkg_path):
                print(f"Couldn't find {package} in {self.clonedir}", mark=3)
                print("Ignoring...", mark=0)
                continue
            g_url = common.process_comm('git', "-C", f"{str(pkg_path)}",
                                        'remote', '-v', fail_handle='report')
            if g_url is None:
                return
            fetch_source = re.compile(r"^.*fetch.*").findall(
                g_url)[0].split(" ")[-2].split("\t")[-1]
            print(f"Deleting {pkg_path}", mark=1)
            print("I can't guess which files were installed.", mark=1)
            print("So, leaving those scars behind...", mark=0)
            print("This project may be added again from the following path",
                  mark=0)
            print(f"{fetch_source}", mark=0)
            shutil.rmtree(pathlib.Path.joinpath(self.clonedir, package))


    def list_proj(self, display=False, grace_exit=True):
        '''
        List all available projects

        Args
            self: Install with this environment
            display: display list of projects
            grace_exit: exit after display?

        '''
        if display:
            for proj in self.git_project_paths.keys():
                g_url = common.process_comm(
                    "git", "-C", f"{str(proj)}", "remote", "-v",
                    fail_handle='report'
                )
                if g_url is None:
                    continue
                if g_url:
                    fetch_source = re.compile(r"^.*fetch.*").findall(
                        g_url)[0].split(" ")[-2].split("\t")[-1],
                    print(
                        str(proj).replace(f'{self.clonedir}/', '') + ":",
                        fetch_source[0], mark='list'
                    )
                else:
                    print(
                        str(proj).replace(f'{self.clonedir}/', '') + ":",
                        'Remote URI Unavailable', mark='warn'
                    )
        if grace_exit:
            sys.exit(0)


    def git_pulls(self) -> None:
        '''
        Pull git projects

        Args:
            self: pull repository in this environment

        '''
        pull_paths = []
        fails = 0
        if self.opt_flags['stale']:
            print("But not trying to update them.", mark=1)
            return

        for git_path, action in self.git_project_paths.items():
            if action.tag & 0x0F == 0x00:
                # Stale flag
                continue
            g_pull = common.process_comm(
                "git", '-C', f'{str(git_path)}', "pull",
                "--recurse-submodules", fail_handle='ignore'
            )
            if g_pull and "Already up to date" not in g_pull:
                print(f"Updating {git_path}", mark=1)
                if any(mark in g_pull for mark in ("+", "-")):
                    self.git_project_paths[git_path].try_install()
                else:
                    fails += 1
                    print(f"Failed in {git_path}", mark=4)
        print()

        for update in pull_paths:
            print(f"Updated code of {update}", mark=3)
        print()
        if fails:
            print(f"{fails} project updates failed", mark=1)
        return
