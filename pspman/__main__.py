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
python module call
'''


import os
import typing
from . import CONFIG, __version__
from .define import prepare_env
from .psprint import print
from .project_actions import (find_gits, end_queues, init_queues, del_projects,
                              add_projects, print_projects, update_projects)


def call() -> int:
    '''
    Parse command line arguments to

        * list cloned git repositories,
        * add / remove git repositories and corresponding installations
        * pull git repositories,
        * update (default),

    Returns:
        error code

    '''
    env_err = prepare_env(CONFIG)
    if env_err != 0:
        return env_err
    if CONFIG.call_function == 'version':
        print(__version__, mark='info')
        return 0

    if CONFIG.verbose:
        print(CONFIG, mark='bug')
    git_projects = find_gits()
    if CONFIG.call_function == 'info':
        return print_projects(git_projects=git_projects)

    queues = init_queues()
    if CONFIG.proj_delete:
        del_projects(git_projects=git_projects, queues=queues,
                     del_list=CONFIG.proj_delete)
    if CONFIG.proj_install:
        add_projects(git_projects=git_projects, queues=queues,
                     to_add_list=CONFIG.proj_install)
    if not CONFIG.stale:
        update_projects(git_projects=git_projects, queues=queues)
    end_queues(queues=queues)
    print()
    print('done.', mark=1)
    return 0


if __name__ == '__main__':
    call()
