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
from datetime import datetime
import shutil
from .tools import timeout
from .tag import ActionTag
from .shell import process_comm
from .installations import (install_make, install_pip,
                            install_meson, install_go)
from .errors import TagError
from . import print


class  InstallEnv():
    '''
    Installation Environment

    Args:
        clone_dir: Directory in which gits are cloned and maintained
        prefix: Directory in which "bin", "share", "lib" are stored
        choices: Choices availed by user {only_pull:, force_risk:, stale:}

    Attributes:
        clone_dir: Path of clone_dir
        prefix: Path to prefix

    '''
    def __init__(self, clone_dir: str, prefix: str = None,
                 choices: dict = None) -> None:
        # options
        self.clone_dir = os.path.realpath(clone_dir)
        if prefix is None:
            prefix = clone_dir
        self.prefix = os.path.realpath(prefix)
        self.choices = choices or {"only_pull": False, "force_risk": False,
                                   "stale": False}

        # initializations

        # Source Code
        os.makedirs(self.clone_dir, exist_ok=True)

        # Installations
        os.makedirs(self.prefix, exist_ok=True)

        # Check permissions for folders
        self.permission_check()

    def permission_check(self) -> None:
        '''
        Check permissions in the given context
        '''
        # Am I root?
        if os.environ["USER"].lower() == "root":
            print("I hate dictators", mark=3)
            if not self.choices.get('force_risk'):
                print("Bye", mark=0)
                sys.exit(2)
            print("I can only hope you know what you are doing...", mark=3)
            print("Here is a chance to kill me in", mark=2)
            timeout(10)
            print("", mark=0)
            print("¯\\_(ツ)_/¯ Your decision ¯\\_(ツ)_/¯", mark=3)
            print("", mark=0)
            print("[INFO] Proceeding...", mark=1)
        else:
            # Is installation directory read/writable
            self.perm_pass(self.clone_dir)
            self.perm_pass(self.prefix)

    @staticmethod
    def perm_pass(permdir: str) -> bool:
        '''
        Args:
            permdir: directory whose permissions are to be checked

        Returns:
            True if all rwx permissions are granted

        '''
        stdout = process_comm("stat", "-L", "-c", "%U %G %a",
                              permdir, fail_handle='report')
        if stdout is None:
            print("Error checking directory permissions, aborting...", mark=5)
            sys.exit(1)
        owner, group, octperm = stdout.replace("\n", "").split(" ")
        if (octperm[-1] == "7") != 0:
            # everyone has access
            return True
        if (octperm[-2] == "7") != 0:
            # some group has permissions
            stdout = process_comm("groups", os.environ["USER"],
                                  fail_handle='report')
            if stdout is None:
                # error
                print("Error checking group permissions, aborting...", mark=5)
                sys.exit(1)
            user_groups = stdout.split(" ")
            for u_grp in user_groups:
                if u_grp == group:
                    return True
        if (octperm[-3] == "7") != 0:
            # owner has permissions
            if os.environ["USER"] == owner:
                return True
        print("We do not have sufficient permissions", mark=5)
        print("Try another location", mark=2)
        print("Bye", mark=0)
        sys.exit(1)
        return False


class GitProject():
    '''
    Git project object.

    Args:
        url: url for git remote
        name: name of project folder
        **kwargs: hard set

            * tag: override with custom tag
            * data: load data

    Attributes:
        url: url for git remote
        path: path of this project
        tag: action tagged to project
        updated: last updated on datetime

    '''
    def __init__(self,
                 env: InstallEnv,
                 url: str = None,
                 name: str = None,
                 **kwargs) -> None:
        self.env = env
        self.updated = None
        self._name = name
        self.url = url
        if 'tag' in kwargs:
            tag = kwargs['tag']
            if isinstance(tag, ActionTag):
                self.a_tag: ActionTag = tag
            else:
                self.a_tag = ActionTag(tag)
        else:
            self.a_tag = ActionTag(0)
        if 'data' in kwargs:
            data = kwargs['data']
            if data is not None:
                self.merge(data)

    def merge(self, data: typing.Dict[str, object]):
        '''
        Update values that are ``None`` or `false` type using data
        '''
        for key, val in data.items():
            self.__dict__[key] = self.__dict__.get(key) or val

    @property
    def path(self):
        return os.path.join(self.env.clone_dir, self.name)

    @property
    def name(self):
        '''
        name of project folder
        '''
        if self._name:
            return self._name
        if self.url is None:
            # This is dangerous, isn't it?
            return None
        self._name =\
            os.path.splitext(self.url.replace(":", "/").split("/")[-1])[0]
        return self._name

    @name.setter
    def name(self, name):
        '''
        :noindex:

        Hard-set name
        '''
        self._name = name

    def type_install(self) -> int:
        if any(os.path.exists(os.path.join(self.path, make_sign)) for
               make_sign in ("Makefile", "configure")):
            self.a_tag.make()
        elif any(os.path.exists(os.path.join(self.path, pip_sign)) for
                 pip_sign in ("setup.py", "setup.cfg")):
            self.a_tag.pip()
        elif os.path.exists(os.path.join(self.path, "meson.build")):
            self.a_tag.meson()
        elif os.path.exists(os.path.join(self.path, "main.go")):
            self.a_tag.goin()
        else:
            self.a_tag
        return self.a_tag.tag // 0x10

    def __repr__(self) -> str:
        '''
        representation of GitProject object
        '''
        return f'''
        *** {self.name} ***
        Last Updated: {self.updated}
        Source: {self.url}
        Base tag: {self.a_tag}
        '''

    def __str__(self) -> str:
        '''
        Print object name

        '''
        return self.name

    def clone(self) -> bool:
        '''
        Get (clone) the remote url

        Returns:
            ``False`` if cloning failed, else, ``True``

        '''
        if self.url is None:
            # clone url is unknown!
            return False
        success = process_comm('git', "-C", self.path, 'clone',
                               self.url, self.name, fail_handle='report')
        if success is None:
            print(f'Cloning source of {self.name} failed', mark='err')
            return False
        self.a_tag.try_install()
        return True

    def update(self) -> bool:
        '''
        Update (pull) source code.
        Success means (Update successful or code is up-to-date)

        Returns:
            ``False`` if update failed, else, ``True``

        '''
        print(f'updating code for {self.path}', mark='info')
        g_pull = process_comm("git", '-C', self.path, "pull",
                              "--recurse-submodules", fail_handle='ignore')
        if g_pull and "Already up to date" not in g_pull:
            if "Updating " in g_pull:
                self.a_tag.try_install()
                print(f"Updated source code of {self}", mark=3)
            else:
                print(f"Failed updating source code of {self}", mark=4)
                return False
        return True

    def install(self) -> bool:
        '''
        Install (update) from source code.

        Returns:
            ``False`` if installation failed, else, ``True``

        '''
        self.type_install()
        print(f'tag: {self.a_tag.tag}', mark='bug')
        install_call: typing.Callable = {
            1: install_make, 2: install_pip, 3: install_meson, 4: install_go,
        }.get(int(self.a_tag.tag//0x10), lambda **_: True)
        if self.a_tag.tag & 0x04:
            return install_call(code_path=self.path, prefix=self.env.prefix)
        return True

    def delete(self) -> None:
        '''
        Delete this project

        '''
        print(f"Deleting {self}", mark=1)
        print("I can't guess which files were installed.", mark=1)
        print("So, leaving those scars behind...", mark=0)
        print("This project may be added again using:", mark=0)
        print(f"pspman -i {self.url}", mark=0)
        shutil.rmtree(self.path)
