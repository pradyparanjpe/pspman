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
import sys
import typing
import pathlib
import re
import yaml
from . import print
from .classes import InstallEnv, GitProject
from .tag import ActionTag
from .shell import process_comm


class CurrentActions:
    '''
    Current actions wrapper object

    Args:
        clone_dir: Clone directory

    Attributes:
        git_projects: git projects to handle
        env: environment

    '''
    def __init__(self, clone_dir: typing.Union[pathlib.Path, str],
                 prefix: typing.Union[pathlib.Path, str] = None,
                 choices: Dict[str, bool] = None):
        self.env: InstallEnv = InstallEnv(clone_dir=clone_dir, prefix=prefix,
                                          choices=choices)
        self.git_projects: typing.Dict[str, GitProject] = {}
        self._load_db()
        self._find_gits()

    def _load_db(self) -> None:
        '''
        Find database file (yml) and load its contents
        '''
        db_path = self.env.clone_dir.joinpath('.psp_db.yml')
        if not os.path.isfile(db_path):
            return
        with open(db_path, 'r') as db_handle:
            db = yaml.safe_load(db_handle)

        # Load Git Projects
        for name, gp_data in db.git_projects.items():
            self.git_projects[name] = GitProject(data=gp_data)


    def _find_gits(self) -> None:
        '''
        Locate git projects in current ``env``
        `Under`rides database

        Returns:
            all project names found in ``env``
        '''
        # discover projects
        discovered_projects: typing.Dict[str, GitProject] = {}
        for leaf in os.listdir(self.env.clone_dir):
            if not os.path.isdir(pathlib.Path.joinpath(
                    self.env.clone_dir, leaf
            )):
                continue
            if not os.path.isdir(
                    pathlib.Path.joinpath(self.env.clonedir, leaf, ".git")
            ):
                continue
            if leaf in self.git_projects:
                continue
            pkg_path = self.env.clone_dir.joinpath(leaf)
            g_url = process_comm('git', "-C", f"{str(pkg_path)}",
                                 'remote', '-v', fail_handle='report')
            url = re.findall(r"^.*fetch.*",
                             g_url)[0].split(" ")[-2].split("\t")[-1]
            discovered_projects[leaf] = GitProject(url=url, name=leaf)
        self.git_projects = {**discovered_projects, **self.git_projects}

    def add_proj(self, to_add_list: typing.List[str]) -> None:
        '''
        Add a project with given url

        Args:
            to_add_list: urls of projects to be added

        '''
        failed_additions = 0
        for url in to_add_list:
            new_project = GitProject(url=url)
            if os.path.isfile(self.env.clone_dir.joinpath(str(new_project))):
                # name is a file, use .d directory
                print(f"A file named '{new_project}' already exists",
                      mark=3)
                new_project.name += ".d"
                print(f"Calling this project '{new_project}'", mark=3)
            if self.git_projects.get(str(new_project)):
                # url leaf has been cloned already
                print(f"{new_project} appears to be installed already", mark=3)
                print(f"I won't overwrite", mark=0)
                continue
            if not new_project.clone():
                failed_additions += 1
                new_project.delete()
                continue
            if not new_project.install():
                failed_additions += 1
                new_project.delete()
                continue
            self.git_projects[new_project.name] = new_project

    def del_proj(self, del_list: typing.List[str]) -> None:
        '''
        Delete given project

        Args:
            del_list: list of names of project directories to be removed
        '''
        for proj_name in del_list:
            if not proj_name in self.git_projects:
                print(f"Couldn't find {proj_name} in {self.env.clone_dir}",
                      mark=3)
                print("Ignoring...", mark=0)
                continue
            project = self.git_projects[proj_name]
            project.delete()

    def list_proj(self):
        '''
        List all available projects

        '''
        print('{projects in self.env.clone_dir}', mark="info")
        for project_name, project in self.git_projects.items():
            if project.url is None:
                print(f"{project_name}: Source URL Unavailable", mark='warn')
            else:
                print(f"{project_name}: {project.url}", mark='list')

    def update_proj(self) -> int:
        '''
        Trigger update for all projects

        '''
        failed_updates = 0
        for project_name, project in self.git_projects.items():
            failed_updates += int(not(project.update()))
        return failed_updates
