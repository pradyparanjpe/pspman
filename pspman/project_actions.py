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
from .shell import git_comm
from .classes import InstallEnv, GitProject
from .queues import (PSPQueue, PullQueue, FailQueue, CloneQueue, SuccessQueue,
                     DeleteQueue, InstallQueue)


def load_db(env: InstallEnv, fname: str) -> typing.Dict[str, GitProject]:
    '''
    Find database file (yml) and load its contents

    Args:
        env: installation context
        fname: name of database file to load

    Returns:
        registered gitprojects

    '''
    db_path = os.path.join(env.clone_dir, fname)
    git_projects: typing.Dict[str, GitProject]= {}
    if not os.path.isfile(db_path):
        if not os.path.isfile(db_path + '.bak'):
            # nothing found
            return git_projects
        # backup exists
        with open(db_path + '.bak', 'r') as db_handle:
             db = yaml.load(db_handle, Loader=yaml.Loader)
    else:
        # database file does exist
        with open(db_path, 'r') as db_handle:
            db = yaml.load(db_handle, Loader=yaml.Loader)

        # Copy a backup
        # Older backup (if it exists) is erased
        os.rename(db_path, db_path + '.bak')

    # Load Git Projects
    for name, gp_data in db.items():
        git_projects[name] = GitProject(data=gp_data)
    return git_projects


def find_gits(
        env: InstallEnv,
        git_projects: typing.Dict[str, GitProject] = None
) -> typing.Dict[str, GitProject]:
    '''
    Locate git projects in the defined `environment` (parse)
    Load database (overrides parser)

    Args:
        env: Installation context
        git_projects: Already known git projects

    Returns:
        all project names found in the `environment`

    '''
    # discover projects
    git_projects = git_projects or {}
    discovered_projects: typing.Dict[str, GitProject] = {}
    healthy_db = load_db(env=env, fname=f'.pspman.healthy.yml')
    fail_db = load_db(env=env, fname=f'.pspman.fail.yml')
    for leaf in os.listdir(env.clone_dir):
        if not os.path.isdir(os.path.join(env.clone_dir, leaf)):
            continue
        if not os.path.isdir(os.path.join(env.clone_dir,
                                          leaf, '.git')):
            continue
        if leaf in git_projects:
            continue
        pkg_path = os.path.join(env.clone_dir, leaf)
        g_url = git_comm(clone_dir=pkg_path, action='list')
        if g_url is None:
            # failed
            continue
        fetch: typing.List[str] = re.findall(r"^.*fetch.*", g_url)
        url = fetch[0].split(' ')[-2].split("\t")[-1].rstrip('/')
        discovered_projects[leaf] = GitProject(url=url, name=leaf)
        discovered_projects[leaf].type_install(env=env)
    git_projects.update({**discovered_projects, **healthy_db, **fail_db})
    return git_projects


def print_projects(env: InstallEnv,
        git_projects: typing.Dict[str, GitProject] = None) -> int:
    '''
    List all available projects

    Args:
        env: Installation context
        git_projects: projects to print

    Returns:
        Error code

    '''
    if git_projects is None or len(git_projects) == 0:
        print("No projects Cloned yet...", mark='warn')
        return 1
    print(f'projects in {env.clone_dir}', end="\n\n", mark='info')
    for project_name, project in git_projects.items():
        if env.verbose:
            print(repr(project), mark='list')
        else:
            if project.url is None:
                print(f"{project_name}:\tSource URL Unavailable",
                      mark='warn')
            else:
                print(f"{project_name}:\t{project.url}", mark='list')
    return 0


def init_queues(env: InstallEnv,) -> typing.Dict[str, PSPQueue]:
    '''
    Initiate success queues

    Args:
        env: Installation context

    '''
    queues: typing.Dict[str, PSPQueue] = {}
    queues['success'] = SuccessQueue(env=env)
    queues['fail'] = FailQueue(env=env)
    queues['install'] = queues['success'] if env.pull\
        else InstallQueue(env=env, success=queues['success'],
                          fail=queues['fail'])
    queues['delete'] = DeleteQueue(env=env,
                                   success=queues['success'],
                                   fail=queues['fail'])
    return queues


def del_projects(env: InstallEnv,
                 git_projects: typing.Dict[str, GitProject],
                 queues: typing.Dict[str, PSPQueue],
                 del_list: typing.List[str] = None) -> None:
    '''
    Delete given project

    Args:
        env: Installation context
        git_projects: known git projects
        queues: initiated queues
        del_list: list of names of project directories to be removed

    '''
    del_list = del_list or []
    for project_name in del_list:
        if project_name not in git_projects:
            print(f"Couldn't find {project_name} in {env.clone_dir}",
                  mark=3)
            print('Ignoring...', mark=0)
            continue
        project = git_projects[project_name]
        queues['delete'].add(project)
    queues['delete'].done()


def _parse_inst(inst_input: str) -> typing.Tuple[str,
                                                 typing.Optional[str],
                                                 typing.List[str],
                                                 typing.Dict[str, str],
                                                 bool]:
    '''
    parse installation string to extract parts
    inst_input is assumed to be of the form:

    Format:
        URL[[[[___branch]___inst_argv]___sh_env]___'only']

    Args:
        URL: str: url to be cloned
        branch: str: custom branch to clone blank implies default
        inst_argv: str: custom arguments these are passed raw
        sh_env: VAR1=VAL1,VAR2=VAL2,VAR3=VAL3...
        pull_only: ``True``, 'hold', 'pull', 'only' => don't install this

    '''
    branch: typing.Optional[str] = None
    sh_env: typing.Dict[str, str] = {}
    inst_argv: typing.List[str] = []
    pull: bool = False
    url, *args = inst_input.split("___")
    if args:
        branch, *args = args
        if args:
            inst_argv_str, *args = args
            inst_argv = inst_argv_str.split(" ")
            if args:
                sh_env_str, *args = args
                for var_val in sh_env_str.split(","):
                    if "=" not in var_val:
                        print(f"{var_val} can't be interpreted as 'var=val'\
ignoring", mark='warn')
                        continue
                    var, val = var_val.split("=")
                    sh_env[var] = val
                if args:
                    pull_str, *args = args
                    if str(pull_str).lower() in ('true', 'pull',
                                                 'only', 'hold'):
                        pull = True
    return url, branch, inst_argv, sh_env, pull

def add_projects(env: InstallEnv,
                 git_projects: typing.Dict[str, GitProject],
                 queues: typing.Dict[str, PSPQueue],
                 to_add_list: typing.List[str] = None) -> None:
    '''
    Add a project with given url

    Args:
        env: Installation context
        git_projects: known git projects
        queues: initiated queues
        to_add_list: urls of projects to be added

    '''
    to_add_list = to_add_list or []
    queues['clone'] = CloneQueue(env=env, success=queues['install'],
                                 fail=queues['fail'])

    for inst_input in to_add_list:
        url, branch, inst_argv, sh_env, pull = _parse_inst(inst_input)
        new_project = GitProject(url=url, sh_env=sh_env,
                                 inst_argv=inst_argv, branch=branch, pull=pull)
        if os.path.isfile(os.path.join(env.clone_dir,
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


def update_projects(env: InstallEnv,
                    git_projects: typing.Dict[str, GitProject],
                    queues: typing.Dict[str, PSPQueue]) -> None:
    '''
    Trigger update for all projects

    Args:
        env: Installation context
        git_projects: known git projects
        queues: initiated queues

    '''
    queues['pull'] = PullQueue(env=env, success=queues['install'],
                               fail=queues['fail'])
    for project in git_projects.values():
        queues['pull'].add(project)
    queues['pull'].done()


def end_queues(env: InstallEnv, queues: typing.Dict[str, PSPQueue]) -> bool:
    '''
    wait (blocking) for queues (threads) to end and return

    Args:
        env: Installation context
        queues: initiated queues
    '''
    # wait for base queues
    for q_name in ('pull', 'clone'):
        if q_name in queues and not queues[q_name].closed:
            if env.verbose:
                print(f'Waiting for {queues[q_name].q_type} queue',
                      mark='bug')
            os.waitpid(queues[q_name].pid, 0)

    # end effect queues
    for q_name in 'delete', 'install':
        if q_name in queues:
            try:
                queues[q_name].done()
            except BrokenPipeError:
                pass
    # wait for term queues
    for q_name in ('success', 'fail'):
        if q_name in queues:
            if env.verbose:
                print(f'Waiting for {queues[q_name].q_type} queue', mark='bug')
            os.waitpid(queues[q_name].pid, 0)

    return True


def interrupt(queues: typing.Dict[str, PSPQueue]):
    '''
    Interrupt actions as they are, kill all children

    Args:
        queues: intitiated queues
    '''
    print('Interrupting...', mark='warn')
    for q_name, child_q in queues.items():
        try:
            child_q.done()
            print(f'Waiting for {child_q.q_type} queue', mark='bug')
            os.waitpid(child_q.pid, 0)
        except BrokenPipeError:
            # child must be dead
            pass
