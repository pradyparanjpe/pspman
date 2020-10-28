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


from os import environ, listdir, getcwd, makedirs
from os.path import isdir
from sys import exit as sysexit
from time import sleep
from subprocess import Popen, PIPE
from pathlib import Path
import pickle as pkl
from psprint import PRINT as print


def timeout(wait: int = 10) -> None:
    '''
    print a count-down time that waits for the process to get killed
    '''
    for time_out in range(wait):
        sleep(1)
        print(f"{wait - time_out:2.0f} seconds...", end="", flush=True, pad=False)
        print("\b" * 13, end="", flush=True, pad=True)
    print(f"{wait:2.0f} seconds...", flush=True, pad=True)


class DirDB():
    '''
    database holding information about clonedir
    '''
    def __init__(self, **kwargs) -> None:
        '''
        clonedir: dir to clone
        prefix: install-prefix
        initialize empty database
        '''
        for key, val in kwargs.items():
            setattr(self, key, val)
        self.install_types = []


class InstallEnv():
    '''
    Installation Environment
    '''
    def __init__(self, clonedir: str, prefix: str, **kwargs):
        '''
        clonedir: Directory in which gits are cloned and maintained
        prefix: Directory in which "bin", "share", "lib" are stored
        force_root: Force installation as ROOT (Administrator)
        only_pull: Don't try to install
        pkg_install: List of new packages to install
        pkg_delete: List of new packages to delete

        '''
        # options
        self.clonedir = Path(clonedir).absolute()
        self.prefix = Path(prefix)
        self.pkg_install = list(kwargs.get("pkg_install", ""))
        self.pkg_delete = list(kwargs.get("pkg_delete", ""))
        self.opt_flags = {"only_pull": False,
                          "force_root": False,
                          "stale": False}
        for key, val in kwargs.items():
            if key in self.opt_flags.keys():
                self.opt_flags[key] = val

        # inits
        makedirs(self.clonedir, exist_ok=True)
        makedirs(self.prefix, exist_ok=True)
        self.git_project_paths = []
        self.base_dir = getcwd()
        self.permission_check()
        self.db = self.read_db(self.clonedir.joinpath(".psp_man_db"))

    def read_db(self, db_file: Path) -> None:
        '''
        update information about software installed in "this" clonedir
        '''
        if db_file.exists():
            with open(db_file, "rb") as database:
                self.db = pkl.load(database)
        else:
            self.db = DirDB(clonedir=self.clonedir, prefix=self.prefix)

    def write_db(self, db_file: Path) -> None:
        '''
        update information about software installed in "this" clonedir
        '''

    def find_gits(self) -> list:
        '''
        locate git projects
        '''
        count = 0
        for leaf in listdir(self.clonedir):
            if isdir(Path.joinpath(self.clonedir, leaf)):
                if isdir(Path.joinpath(self.clonedir, leaf, ".git")):
                    self.git_project_paths.append(
                        Path.joinpath(self.clonedir, leaf)
                    )
                    count += 1
        print(f"{count} project(s) found in {str(self.clonedir)}", pref=1, pad=True)

    def permission_check(self) -> None:
        '''
        check permissions in the given context
        '''
        # Am I root?
        if environ["USER"].lower() == "root":
            print("I hate dictators", pref=3, pad=True)
            if not self.opt_flags['force_root']:
                print("Bye", pref=0, pad=True)
                sysexit(2)
            print("I can only hope you know what you are doing...", pref=3, pad=True)
            print("Here is a chance to kill me in", pref=2, pad=True)
            timeout(10)
            print("", pref=0, pad=True)
            print("¯\_(ツ)_/¯ Your decision ¯\_(ツ)_/¯", pref=3, pad=True)
            print("", pref=0, pad=True)
            print("[INFO] Proceeding...", pref=1, pad=True)
        else:
            # Is installation directory read/writable
            parentdir = Path(self.clonedir)
            while not isdir(parentdir):
                parentdir = Path(parentdir).parent
            self.perm_pass(parentdir)
            self.perm_pass(self.prefix)

    @staticmethod
    def perm_pass(permdir: str) -> None:
        '''
        permdir: directory whose permissions are to be checked
        returns: True if all rwx permissions are granted
        '''
        call = Popen(["stat", "-L", "-c", "%U %G %a", permdir],
                     stderr=PIPE, stdout=PIPE, text=True)
        stdout, stderr = call.communicate()
        if stderr:
            print(f"{stderr}", pref=4, pad=True)
            print("aborting...", pref=4, pad=True)
            sysexit()
        owner, group, octperm = stdout.replace("\n", "").split(" ")
        if (octperm[-1] == "7") != 0:
            # everyone has access
            return True
        if (octperm[-2] == "7") != 0:
            # some group has permissions
            call = Popen(["groups", environ["USER"]],
                         stderr=PIPE, stdout=PIPE, text=True)
            stdout, stderr = call.communicate()
            user_groups = stdout.split(" ")
            for u_grp in user_groups:
                if u_grp == group:
                    return True
        if (octperm[-3] == "7") != 0:
            # owner has permissions
            if environ["USER"] == owner:
                return True
        print("We do not have sufficient permissions", pref=4, pad=True)
        print("Try another location", pref=2, pad=True)
        print("Bye", pref=0, pad=True)
        sysexit(1)
        return False
