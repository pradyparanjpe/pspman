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
from . import CONFIG
from .psprint import print
from .shell import git_comm
from .classes import GitProject, PSPManDB
from .queues import (PSPQueue, SuccessQueue, FailQueue, DeleteQueue,
                     PullQueue, CloneQueue, InstallQueue)


def find_gits(git_projects: typing.Dict[str, GitProject]
               = None) -> typing.Dict[str, GitProject]:
    '''
    Locate git projects in the defined `environment` (parse)
    Load database (overrides parser)

    Args:
        git_projects: Already known git projects

    Returns:
        all project names found in the `environment`

    '''
    # discover projects
    git_projects = git_projects or {}
    discovered_projects: typing.Dict[str, GitProject] = {}
    read_db = PSPManDB()
    read_db.load_db()
    for leaf in os.listdir(CONFIG.clone_dir):
        if not os.path.isdir(os.path.join(CONFIG.clone_dir, leaf)):
            continue
        if not os.path.isdir(os.path.join(CONFIG.clone_dir,
                                          leaf, '.git')):
            continue
        if leaf in git_projects:
            continue
        pkg_path = os.path.join(CONFIG.clone_dir, leaf)
        g_url = git_comm(clone_dir=pkg_path, action='list')
        if g_url is None:
            # failed
            continue
        fetch: typing.List[str] = re.findall(r"^.*fetch.*", g_url)
        url = fetch[0].split(' ')[-2].split("\t")[-1].rstrip('/')
        discovered_projects[leaf] = GitProject(url=url, name=leaf)
        discovered_projects[leaf].type_install()
    git_projects.update({**discovered_projects, **read_db.git_projects})
    return git_projects


def print_projects(git_projects: typing.Dict[str, GitProject] = None) -> int:
    '''
    List all available projects

    Args:
        git_projects: projects to print

    Returns:
        Error code

    '''
    if git_projects is None or len(git_projects) == 0:
        print("No projects Cloned yet...", mark='warn')
        return 1
    print(f'projects in {CONFIG.clone_dir}', end="\n\n", mark='info')
    for project_name, project in git_projects.items():
        if CONFIG.verbose:
            print(repr(project), mark='list')
        else:
            if project.url is None:
                print(f"{project_name}:\tSource URL Unavailable",
                      mark='warn')
            else:
                print(f"{project_name}:\t{project.url}", mark='list')
    return 0


def init_queues() -> typing.Dict[str, PSPQueue]:
    '''
    Initiate success queues

    '''
    queues: typing.Dict[str, PSPQueue] = {}
    queues['success'] = SuccessQueue()
    queues['fail'] = FailQueue()
    queues['install'] = queues['success'] if CONFIG.pull\
        else InstallQueue(success=queues['success'], fail=queues['fail'])
    queues['delete'] = DeleteQueue(success=queues['success'],
                                   fail=queues['fail'])
    return queues


def del_projects(git_projects: typing.Dict[str, GitProject],
                 queues: typing.Dict[str, PSPQueue],
                 del_list: typing.List[str] = None) -> None:
    '''
    Delete given project

    Args:
        git_projects: known git projects
        queues: initiated queues
        del_list: list of names of project directories to be removed

    '''
    del_list = del_list or []
    for project_name in del_list:
        if project_name not in git_projects:
            print(f"Couldn't find {project_name} in {CONFIG.clone_dir}",
                  mark=3)
            print('Ignoring...', mark=0)
            continue
        project = git_projects[project_name]
        queues['delete'].add(project)
    queues['delete'].done()


def add_projects(git_projects: typing.Dict[str, GitProject],
                 queues: typing.Dict[str, PSPQueue],
                 to_add_list: typing.List[str] = None) -> None:
    '''
    Add a project with given url

    Args:
        git_projects: known git projects
        queues: initiated queues
        to_add_list: urls of projects to be added

    '''
    to_add_list = to_add_list or []
    queues['clone'] = CloneQueue(success=queues['install'],
                                      fail=queues['fail'])

    for url in to_add_list:
        new_project = GitProject(url=url)
        if os.path.isfile(os.path.join(CONFIG.clone_dir,
                                       new_project.name)):
            # name is a file, use .d directory
            print(f"A file named '{new_project}' already exists", mark=3)
            new_project.name += '.d'
            print(f"Calling this project '{new_project}'", mark=3)
        if git_projects.get(str(new_project)):
            # url leaf has been cloned already
            print(f"{new_project} appears to be installed already", mark=3)
            print("I won't overwrite", mark=0)
            continue
        queues['clone'].add(new_project)
    queues['clone'].done()


def update_projects(git_projects: typing.Dict[str, GitProject],
                    queues: typing.Dict[str, PSPQueue]) -> None:
    '''
    Trigger update for all projects

    Args:
        git_projects: known git projects
        queues: initiated queues

    '''
    queues['pull'] = PullQueue(success=queues['install'],
                                    fail=queues['fail'])
    for project_name, project in git_projects.items():
        queues['pull'].add(project)
    queues['pull'].done()


def end_queues(queues: typing.Dict[str, PSPQueue]) -> bool:
    '''
    wait (blocking) for queues (threads) to end and return

    Args:
        queues: initiated queues
    '''
    for q_name in ('success', 'fail'):
        if q_name in queues:
            os.waitpid(queues[q_name].pid, 0)
    return True
