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
Environment Classes
'''


from os import environ, listdir, getcwd, makedirs
from os.path import isdir
from sys import exit as sysexit
from time import sleep
from subprocess import Popen, PIPE
from pathlib import Path
from .input_output import print_info


def timeout(wait: int = 10) -> None:
    '''
    print a count-down time that waits for the process to get killed
    '''
    for time_out in range(wait):
        sleep(1)
        print(f"{wait - time_out:2.0f} seconds...", end="", flush=True)
        print("\b" * 13, end="", flush=True)
    print(f"{wait:2.0f} seconds...", flush=True)


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
        self.clonedir = Path(clonedir)
        self.prefix = Path(prefix)
        if not clonedir.exists():
            makedirs(clonedir, exist_ok=True)
        if not prefix.exists():
            makedirs(prefix, exist_ok=True)
        self.only_pull = kwargs["only_pull"]
        self.force_root = kwargs["force_root"]
        self.pkg_install = list(kwargs.get("pkg_install", ""))
        self.pkg_delete = list(kwargs.get("pkg_delete", ""))
        self.base_dir = getcwd()
        self.git_project_paths = []
        self.permission_check()

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
        print_info(f"{count} project(s) found in {str(self.clonedir)}", 1)

    def permission_check(self) -> None:
        '''
        check permissions in the given context
        '''
        # Am I root?
        if environ["USER"].lower() == "root":
            print_info("I hate dictators", 3)
            if not self.force_root:
                print_info("Bye", 0)
                sysexit(2)
            print_info("I can only hope you know what you are doing...", 3)
            print_info("Here is a chance to kill me in", 2)
            timeout(10)
            print_info("", 0)
            print_info("¯\_(ツ)_/¯ Your decision ¯\_(ツ)_/¯", 3)
            print_info("", 0)
            print_info("[INFO] Proceeding...", 1)
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
            print_info(f"{stderr}", 4)
            print_info("aborting...", 4)
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
        print_info("We do not have sufficient permissions", 4)
        print_info("Try another location", 2)
        print_info("Bye", 0)
        sysexit(1)
        return False
