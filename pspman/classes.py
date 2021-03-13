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
object classes

'''


import os
import typing
import re
from datetime import timezone, datetime
import json
import yaml
from psprint import print
from .tag import ACTION_TAG
from .errors import TagError, GitURLError


class InstallEnv():
    '''
    Installation variables

    Attributes:
        call_function: sub-function called {version,info,unlock}
        clone_dir: base directory to clone src
        prefix: [=``clone_dir``] `prefix` for installation
        risk: risk root
        pull: only pull, don't try to install
        stale: do not update, only delete/install new
        verbose: print semi-verbose output
        install: install (clone) from remote urls
        delete: delete projects


    Args:
        **kwargs: hard set `attributes`

    '''
    def __init__(self, **kwargs):
        self.call_function: typing.Optional[str] = None
        self._clone_dir: typing.Optional[str] = None
        self._prefix: typing.Optional[str] = None
        self.risk: bool = False
        self.pull: bool = False
        self.stale: bool = False
        self.verbose: bool = False
        self.install: typing.List[str] = []
        self.delete: typing.List[str] = []
        self.update(kwargs)

    @property
    def prefix(self) -> str:
        if self._prefix is None:
            self._prefix = os.path.join(os.environ['HOME'], ".pspman")
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self._prefix = value

    @prefix.deleter
    def prefix(self):
        self._prefix = os.path.join(os.environ['HOME'], ".pspman")

    @property
    def clone_dir(self) -> str:
        if self._clone_dir is None:
            return os.path.join(self.prefix, 'src')
        return self._clone_dir

    @clone_dir.setter
    def clone_dir(self, value):
        self._clone_dir = value

    @clone_dir.deleter
    def clone_dir(self):
        self._clone_dir = None

    def __repr__(self) -> str:
        return  f'''
        Clone Directory: {self.clone_dir}
        Prefix: {self.prefix}

        Called sub-function: {self.call_function}
        Deletions Requested: {len(self.delete)}
        Additions requested: {len(self.install)}

        Optional Flags:
        Risk Root: {self.risk}
        Only Pull: {self.pull}
        Don't Update: {self.stale}
        Verbose Debugging: {self.verbose}

        '''

    def update(self, options: typing.Dict[str, object]) -> 'InstallEnv':
        '''
        Update attributes with those from options
        '''
        for key, value in options.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


class GitProject():
    '''
    Git project object.

    Args:
        url: url for git remote
        name: name of project folder
        **kwargs: hard set

            * tag: int: override with custom tag
            * data: Dict[str, Any]: load data
            * branch: str: git branch to be cloned
            * sh_env: Dict[str, str]: shell env alterations for installation
            * inst_argv: List[str]: arguments suffixed to optional args
            * rest are ignored

    Attributes:
        url: url for git remote
        name: name of project folder
        tag: action tagged to project
        branch: git branch to be cloned
        sh_env: environ modifications before installation
        inst_argv: arguments suffixed to optional args before positional args
        pull: only pull this project, don't run install scripts
        last_updated: last updated on datetime

    '''
    def __init__(self,
                 url: str = None,
                 name: str = None,
                 **kwargs) -> None:
        self.url = url
        self.tag = int(kwargs['tag']) if 'tag' in kwargs else 0
        self.branch: typing.Optional[str] = kwargs.get('branch')
        self.last_updated: typing.Optional[float] = None
        self.inst_argv: typing.List[str] = kwargs.get('inst_argv', [])
        self.sh_env: typing.Dict[str, str] = kwargs.get('sh_env', {})
        self.pull: bool = False
        if kwargs.get('data') is not None:
            self.merge(kwargs['data'])
        self.name = name or self.update_name()

    def update_name(self) -> str:
        '''
        Update project name.
        Call this method after updating ``url``

        Returns:
            The updated name
        '''
        if hasattr(self, 'name'):
            return self.name
        if self.url is None:
            raise GitURLError
        self.name = os.path.splitext(
            self.url.replace(':', '/').split('/')[-1]
        )[0]
        return self.name

    def merge(self, data: typing.Dict[str, object]) -> None:
        '''
        Update values that are ``None`` type using ``data``.
        Doesn't change set values

        Args:
            data: source for update

        '''
        for key, val in data.items():
            self.__dict__[key] = self.__dict__.get(key) or val

    def type_install(self, env: InstallEnv) -> None:
        '''
        Determine guess the installation type based on files present
        in the cloned directory

        Args:
            env: context in which, type of installation is called
        '''
        if env.pull or self.pull:
            self.tag &= 0x0F
            return
        if self.name is None:
            if self.update_name() is None:
                raise GitURLError()
        path = os.path.join(env.clone_dir, self.name)
        if any(os.path.exists(os.path.join(path, make_sign)) for
               make_sign in ('Makefile', 'configure')):
            self.tag |= ACTION_TAG['make']
        elif any(os.path.exists(os.path.join(path, pip_sign)) for
                 pip_sign in ('setup.py', 'setup.cfg')):
            self.tag |= ACTION_TAG['pip']
        elif os.path.exists(os.path.join(path, 'meson.build')):
            self.tag |= ACTION_TAG['meson']
        elif os.path.exists(os.path.join(path, 'main.go')):
            self.tag |= ACTION_TAG['go']
        else:
            self.tag &= 0x0F

    def mark_update_time(self):
        '''
        Mark that the project was updated

        '''
        self.last_updated = datetime.now().timestamp()

    def __repr__(self) -> str:
        '''
        representation of GitProject object
        '''
        updated = datetime.fromtimestamp(self.last_updated)\
            if self.last_updated else None
        return f'''
        *** {self.name} ***
        Last Updated: {updated}
        Source: {self.url}
        Branch: {self.branch}
        Installation arguments: {self.inst_argv}
        Altered shell environment variables: {self.sh_env}
        Base tag: {hex(self.tag)}
        Pull: {self.pull}
        '''

    def __str__(self) -> str:
        '''
        Print object name

        '''
        return str(self.name)


class GitProjectListEncoder(json.JSONEncoder):
    '''
    Encode Class object's __dict__

    '''
    def default(self, o: GitProject) -> dict:
        return o.__dict__



