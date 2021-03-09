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
from datetime import datetime
import json
import yaml
from . import CONFIG
from .psprint import print
from .tag import ACTION_TAG
from .shell import process_comm
from .errors import TagError, GitURLError


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
        name: name of project folder
        tag: action tagged to project
        last_updated: last updated on datetime

    '''
    def __init__(self,
                 url: str = None,
                 name: str = None,
                 **kwargs) -> None:
        self.url = url
        self.tag = int(kwargs['tag']) if 'tag' in kwargs else 0
        self.last_updated: typing.Optional[datetime] = None
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

    def type_install(self) -> None:
        '''
        Determine guess the installation type based on files present
        in the cloned directory

        '''
        if self.name is None:
            if self.update_name() is None:
                raise GitURLError()
        path = os.path.join(CONFIG.clone_dir, self.name)
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
        self.last_updated = datetime.now()

    def __repr__(self) -> str:
        '''
        representation of GitProject object
        '''
        return f'''
        *** {self.name} ***
        Last Updated: {self.last_updated}
        Source: {self.url}
        Base tag: {hex(self.tag)}
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


class PSPManDB():
    '''
    Database to store and load database

    Attributes:
        git_projects: list of database project
        fname: fname

    Args:
        git_projects: project
        fname: fname

    '''

    def __init__(self,
                 git_projects: typing.Dict[str, GitProject] = None,
                 fname: str = '.pman_db.yml') -> None:
        self.git_projects = git_projects or {}
        self.fname = fname

    def load_db(self) -> None:
        '''
        Find database file (yml) and load its contents

        '''
        db_path = os.path.join(CONFIG.clone_dir, self.fname)
        if not os.path.isfile(db_path):
            return
        with open(db_path, 'r') as db_handle:
            db = yaml.load(db_handle, Loader=yaml.Loader)

        # Load Git Projects
        for name, gp_data in db.get('git_projects', {}).items():
            self.git_projects[name] = GitProject(data=gp_data)

    def save_db(self) -> None:
        '''
        Save current information as yaml database file

        '''
        # Human readable is more transparent than easily decodable encoding
        db_path = os.path.join(CONFIG.clone_dir, '.psp_db.yml')
        if os.path.isfile(db_path):
            # old database file does exist
            # Copy a backup
            # Older backup (if it exists) is erased
            os.rename(db_path, db_path + '.bak')
        gp_data = {}
        # dump git projects' data attributes
        for name, project in self.git_projects.items():
            gp_data[name] = project.__dict__
        with open(db_path, 'w') as db_handle:
            yaml.dump({'git_projects': gp_data}, db_handle)
