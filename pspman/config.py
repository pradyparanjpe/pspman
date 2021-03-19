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
Read configuration

'''


import os
import typing
import yaml
from .errors import PathNameError


def _config_dir(path: str = None) -> str:
    '''
    Guess the default configuration path based on XDG_CONFIG_HOME variable
    Following paths are checked in order until a feasable target is found

        * ``path``
        * ${XDG_CONFIG_HOME}/pspman
        * ${HOME}/.config/pspman
        * ${HOME}/.pspman
        * ${PWD}/.pspman

    Args:
        path: recommended config directory

    Returns:
        Path to config dir

    '''
    if path:
        if os.path.isdir(path):
            # Deliberately not creating anew
            return path
        else:
            err_str = f"Configuration path '{path}' does not exist."\
                + f"Do you mean {os.path.split(path)[0]}?"
            raise FileNotFoundError(err_str)
    config_dir = os.environ.get('XDG_CONFIG_HOME')
    if config_dir is not None:
        config_path = os.path.join(config_dir, 'pspman')
        os.makedirs(config_path, exist_ok=True)
        return config_path
    home_dir = os.environ.get('HOME')
    if home_dir is None:
        # On which wierd operating system is this installed?
        config_path = ".pspman"
        os.makedirs(config_path, exist_ok=True)
        return ".pspman"
    config_dir = os.path.join(home_dir, '.config')
    config_path = os.path.join(config_dir, 'pspman')
    if os.path.isdir(config_dir):
        os.makedirs(config_path, exist_ok=True)
        return config_path
    config_path = os.path.join(home_dir, '.pspman')
    os.makedirs(config_path, exist_ok=True)
    return config_path


def _data_dir(path: str = None) -> str:
    '''
    Guess the default data path based on XDG_DATA_HOME variable
    Following paths are checked in order until a feasable target is found

        * ``path``
        * ${XDG_DATA_HOME}/pspman
        * ${HOME}/.local/share/pspman
        * ${HOME}/.pspman
        * ${PWD}/.pspman

    Args:
        path: recommended data directory

    Returns:
        path to config dir

    '''
    if path:
        if os.path.isdir(path):
            # Deliberately not creating anew
            return path
        else:
            err_str = f"Data path '{path}' does not exist." + \
                f"Do you mean {os.path.split(path)[0]}?"
            raise FileNotFoundError(err_str)
    data_dir = os.environ.get('XDG_DATA_HOME')
    if data_dir is not None:
        data_path = os.path.join(data_dir, 'pspman')
        os.makedirs(data_path, exist_ok=True)
        return data_path
    home_dir = os.environ.get('HOME')
    if home_dir is None:
        # On which wierd operating system is this installed?
        data_path = ".pspman"
        os.makedirs(data_path, exist_ok=True)
        return ".pspman"
    data_dir = os.path.join(home_dir, '.local', 'share')
    data_path = os.path.join(data_dir, 'pspman')
    if os.path.isdir(data_dir):
        os.makedirs(data_path, exist_ok=True)
        return data_path
    data_path = os.path.join(home_dir, '.pspman')
    os.makedirs(data_path, exist_ok=True)
    return data_path


class GroupDB():
    '''
    Group database information

    Args:
        **kwargs:

            * data: create object using data as __dict__
            * arg in Attributes: Hard-set attributes
            * rest are ignored

    Attributes:
        path: path to Group
        name: custom-name for group [default: leaf of path]
        exists: whether path exists os.exists
        clone_type: type of clones (0[default], -1, 1)

            * 1: all projects are installable
            * -1: no project is installable (all are pull-only)
            * 0: heterogenous

    '''
    def __init__(self, **kwargs):
        self.path: str
        self._path: typing.Optional[str] = kwargs.get('path')
        self.clone_type = int(kwargs.get('clone_type', 0))

        # Infer from parent.__dict__
        if 'data' in kwargs:
            self.merge(kwargs['data'])
            del kwargs['data']

        self.name = str(kwargs.get('name', self.get_name()))

    @property
    def locked(self) -> bool:
        if os.path.isfile(os.path.join(self.path, '.proc.lock')):
            return True
        return False

    @locked.setter
    def locked(self, val):
        # Do nothing, shouldn't get hard-set
        return

    @locked.deleter
    def locked(self):
        # Do nothing, shouldn't get hard-set
        return

    @property
    def path(self) -> str:
        if self._path:
            return os.path.abspath(self._path)
        raise ValueError('Value for path not provided')

    @path.setter
    def path(self, value: str):
        self._path = os.path.abspath(value)

    @property
    def exists(self) -> bool:
        if self.path is None:
            return False
        return os.path.isdir(self.path)

    @exists.setter
    def exists(self, val):
        # Do nothing, shouldn't get hard-set
        return

    @exists.deleter
    def exists(self):
        # Do nothing, shouldn't get hard-set
        return

    def get_name(self) -> str:
        '''
        Infer name from filepath
        '''
        if hasattr(self, 'name'):
            return self.name
        if self.path is None:
            raise PathNameError()
        return os.path.split(self.path)[-1]

    def mk_structure(self):
        '''
        Generate a directory structure for the GitGroup
        '''
        os.makedirs(self.path, exist_ok=True)
        dir_struct = ("bin", "etc", "include", "lib", "lib64", "libexec",
                      "programs", "share", "src", "tmp", "usr")
        for workdir in dir_struct:
            os.makedirs(os.path.join(self.path, workdir), exist_ok=True)

    def merge(self, data: typing.Dict[str, object]) -> None:
        '''
        Update values that are ``None`` type using ``data``.
        Doesn't change set values

        Args:
            data: source for update

        '''
        for key, val in data.items():
            setattr(self, key, self.__dict__.get(key) or val)

    def __repr__(self) -> str:
        '''
        Representation
        '''
        clone_type = ('heterogenous',  'install', 'pull-only')[self.clone_type]
        locked = ('No', 'Yes')[int(self.locked)]
        return f'''
        name: {self.name}
        path: {self.path}
        exists: {self.exists}
        locked: {locked}
        clone_type: {clone_type}
        '''

class MetaConfig():
    '''
    Meta-Config bearing information about all GroupDBs

    Args:
        kwargs:

            * arg in Attributes: Hard-set attributes
            * rest are ignored

    Attributes:
        meta_db_dirs: registry of all GroupDBs
        config_dir: pspman configuration directory
        data_dir: pspman default data directory

    '''
    def __init__(self, **kwargs):
        self.meta_db_dirs: typing.Dict[str, GroupDB] = {}
        self.config_dir = _config_dir(kwargs.get('config_dir'))
        self.data_dir = _data_dir(kwargs.get('data_dir'))
        for group in kwargs.get('meta_db_dirs', {}).values():
            self.add(group)

    def add(self, group: typing.Union[GroupDB, dict]):
        '''
        Add (don't overwrite) Group

        Args:
            group: Group (or its __dict__) to be added
        '''
        if isinstance(group, dict):
            group = GroupDB(data=group)
        if group.name in self.meta_db_dirs:
            return
        if group.path == self.data_dir and group.name != 'default':
            # Default prefix
            return
        self.meta_db_dirs[group.name] = group

    def remove(self, name: str):
        '''
        Remove group

        Args:
            name: name of group to remove

        '''
        if name in self.meta_db_dirs:
            del self.meta_db_dirs[name]

    def prune(self):
        '''
        If any group doesn't exist anymore, remove it
        '''
        zombies: typing.List[str] = []
        for name, group in self.meta_db_dirs.items():
            if not group.exists:
                zombies.append(name)
        for name in zombies:
            self.remove(name)

    def load(self, psp_config: str) -> bool:
        '''
        Load meta configuration

        Args:
            psp_config: yaml file containing GroupDB meta data

        Returns:
            ``True`` if file was successfully loaded
        '''
        if not os.path.isfile(psp_config):
            return False
        with open(psp_config, 'r') as conf_fh:
            groups_data: typing.Dict[str, dict] = yaml.safe_load(conf_fh)
        for group in groups_data.values():
            self.add(group)
        return True

    def store(self):
        '''
        Refresh a configuration file

        Args:
            psp_config: path to pspman config file (yml)

        '''
        psp_config = os.path.join(self.config_dir, 'config.yml')
        with open(psp_config, 'w') as conf_fh:
            for group_name, group_db in self.meta_db_dirs.items():
                yaml.dump({group_name: group_db.__dict__}, conf_fh)


def read_config(path: str = None) -> MetaConfig:
    '''
    Read and maintain default configurations

    Args:
        path: path to file containing configurations

    Returns:
        Configuration
    '''
    psp_config = os.path.join(_config_dir(), 'config.yml')
    config = MetaConfig()
    if config.load(psp_config):
        config.prune()
        return config
    init_msg = [
        'PSPMan is not initialized',

        "To initialize: run without ' #':",
        "\033[0;97;40m" + "pspman init" + "\033[0m:"
    ]
    print("\n    ".join(init_msg))
    return config
