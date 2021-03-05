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
Actions on projects, other than automated installations

'''


import os
import typing
import re
import yaml
from . import print
from .queues import (PSPQueue, SuccessQueue, FailQueue, DeleteQueue,
                     PullQueue, CloneQueue, InstallQueue)
from .classes import InstallEnv, GitProject, PSPManDB
from .shell import git_comm


class CurrentActions:
    '''
    Current actions wrapper object

    Attributes:
        git_projects: git projects to handle
        env: environment
        choices: optional choices

    Args:
        clone_dir: Clone directory
        prefix: Prefix location: contains bin, lib, include
        choices: Choices for `list`, `pull only`, `force_risk`

    '''
    def __init__(self, clone_dir: str, prefix: str = None,
                 choices: typing.Dict[str, bool] = None):
        self.choices = choices or {}
        self.env: InstallEnv = InstallEnv(clone_dir=clone_dir, prefix=prefix,
                                          choices=choices)
        self.git_projects: typing.Dict[str, GitProject] = {}
        self._find_gits()
        self.git_projects

        # Queues
        self.queues: typing.Dict[str, PSPQueue] = {}

    def _init_queues(self):
        '''
        initiate queues
        '''
        self.queues['success'] = SuccessQueue(env=self.env)
        self.queues['fail'] = FailQueue(env=self.env)
        self.queues['install'] = self.queues['success'] \
            if self.choices.get('only_pull', False)\
               else InstallQueue(env=self.env,
                                 success=self.queues['success'],
                                 fail=self.queues['fail'])

    def _find_gits(self) -> None:
        '''
        Locate git projects in current ``env`` (parse)
        Load database (overrides parser)

        Returns:
            all project names found in ``env``

        '''
        # discover projects
        discovered_projects: typing.Dict[str, GitProject] = {}
        read_db = PSPManDB(env=self.env)
        read_db.load_db()
        for leaf in os.listdir(self.env.clone_dir):
            if not os.path.isdir(os.path.join(self.env.clone_dir, leaf)):
                continue
            if not os.path.isdir(os.path.join(self.env.clone_dir,
                                              leaf, '.git')):
                continue
            if leaf in self.git_projects:
                continue
            pkg_path = os.path.join(self.env.clone_dir, leaf)
            g_url = git_comm('list', pkg_path)
            if g_url is None:
                # failed
                continue
            fetch: typing.List[str] = re.findall(r"^.*fetch.*", g_url)
            url = fetch[0].split(' ')[-2].split("\t")[-1].rstrip('/')
            discovered_projects[leaf] = GitProject(url=url, name=leaf)
            discovered_projects[leaf].type_install(env=self.env)
        self.git_projects = {**discovered_projects, **read_db.git_projects}

    def list_projects(self):
        '''
        List all available projects

        '''
        print(f'projects in {self.env.clone_dir}', end="\n\n", mark='info')
        for project_name, project in self.git_projects.items():
            if self.choices.get('verbose', False):
                print(repr(project), mark='list')
            else:
                if project.url is None:
                    print(f"{project_name}:\tSource URL Unavailable",
                          mark='warn')
                else:
                    print(f"{project_name}:\t{project.url}", mark='list')

    def del_projects(self, del_list: typing.List[str]) -> None:
        '''
        Delete given project

        Args:
            del_list: list of names of project directories to be removed

        '''
        if 'success' not in self.queues:
            self._init_queues()
        self.queues['delete'] = DeleteQueue(env=self.env,
                                            success=self.queues['success'],
                                            fail=self.queues['fail'])
        for project_name in del_list:
            if project_name not in self.git_projects:
                print(f"Couldn't find {project_name} in {self.env.clone_dir}",
                      mark=3)
                print('Ignoring...', mark=0)
                continue
            project = self.git_projects[project_name]
            self.queues['delete'].add(project)
        self.queues['delete'].done()

    def add_projects(self, to_add_list: typing.List[str]) -> None:
        '''
        Add a project with given url

        Args:
            to_add_list: urls of projects to be added

        '''
        if 'success' not in self.queues:
            self._init_queues()
        self.queues['clone'] = CloneQueue(env=self.env,
                                          success=self.queues['install'],
                                          fail=self.queues['fail'])

        for url in to_add_list:
            new_project = GitProject(url=url)
            if os.path.isfile(os.path.join(self.env.clone_dir,
                                           new_project.name)):
                # name is a file, use .d directory
                print(f"A file named '{new_project}' already exists", mark=3)
                new_project.name += '.d'
                print(f"Calling this project '{new_project}'", mark=3)
            if self.git_projects.get(str(new_project)):
                # url leaf has been cloned already
                print(f"{new_project} appears to be installed already", mark=3)
                print("I won't overwrite", mark=0)
                continue
            self.queues['clone'].add(new_project)
        self.queues['clone'].done()

    def update_projects(self) -> None:
        '''
        Trigger update for all projects

        '''
        if 'success' not in self.queues:
            self._init_queues()
        self.queues['pull'] = PullQueue(env=self.env,
                                        success=self.queues['install'],
                                        fail=self.queues['fail'])
        for project_name, project in self.git_projects.items():
            self.queues['pull'].add(project)
        self.queues['pull'].done()
