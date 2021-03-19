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
from .config import MetaConfig
from .tag import ACTION_TAG
from .errors import TagError, GitURLError


class InstallEnv():
    '''
    Installation variables

    Attributes:
        call_function: sub-function called {version,info,meta,unlock}
        clone_dir: base directory to clone src
        prefix: `prefix` for installation
        risk: risk root
        pull: only pull, don't try to install
        stale: do not update, only delete/install new
        verbose: print semi-verbose output
        install: install (clone) from remote urls
        delete: delete projects


    Args:
        config: MetaConfig to determine default values
        **kwargs: hard set `attributes`

    '''
    def __init__(self, config: MetaConfig, **kwargs):
        self.call_function: typing.Optional[str] = kwargs.get('call_function')
        self._clone_dir: typing.Optional[str] = kwargs.get('clone_dir')
        self.prefix: str = kwargs.get('prefix', config.data_dir)
        self.risk: bool = kwargs.get('risk', False)
        self.pull: bool = kwargs.get('pull', False)
        self.stale: bool = kwargs.get('stale', False)
        self.verbose: bool = kwargs.get('verbose', False)
        self.install: typing.List[str] = kwargs.get('install', [])
        self.delete: typing.List[str] =  kwargs.get('delete', [])

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

        Args:
            options: hard-set config
        '''
        for key, value in options.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self


class GitProject():
    '''
    Git project object.

    Args:
        **kwargs:

            * args corresponding to Attributes: hard set
            * data: Dict[str, Any]: load data
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
    def __init__(self, **kwargs) -> None:
        self.url: str = kwargs.get('url', None)
        self.tag = int(kwargs.get('tag', 0))
        self.branch: typing.Optional[str] = kwargs.get('branch')
        self.last_updated: typing.Optional[float] = kwargs.get('last_updated')
        self.inst_argv: typing.List[str] = kwargs.get('inst_argv', [])
        self.sh_env: typing.Dict[str, str] = kwargs.get('sh_env', {})
        self.pull: bool = kwargs.get('pull', False)

        # Infer from parent.__dict__
        if kwargs.get('data') is not None:
            self.merge(kwargs['data'])
            del kwargs['data']

        self.name: str = kwargs.get('name', self.update_name())

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
        self.name = os.path.splitext(self.url.replace(':', '/')
                                     .split('/')[-1])[0]
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
        in the cloned directory.

        Args:
            env: context in which, type_install is called.
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
        elif os.path.exists(os.path.join(path, 'CMakeLists.txt')):
            self.tag |= ACTION_TAG['cmake']
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
        Source: {self.url}
        Branch: {self.branch}
        Last Updated: {updated}
        Only Pull?: {self.pull}
        Base tag: {hex(self.tag)}
        Installation arguments: {self.inst_argv}
        Altered shell environment variables: {self.sh_env}
        '''

    def __str__(self) -> str:
        '''
        Print object name

        '''
        return str(self.name)


class GitProjEncoder(json.JSONEncoder):
    '''
    Encode Class object's __dict__

    '''
    def default(self, o: GitProject) -> dict:
        return o.__dict__
