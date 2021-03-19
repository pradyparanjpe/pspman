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
from .psp_in import init, de_init
from .config import GroupDB
from . import ENV, CONFIG, print, __version__
from .define import cli_opts, prepare_env, lock
from .serial_actions import (interrupt, find_gits, end_queues, init_queues,
                             del_projects, add_projects, print_projects,
                             update_projects, print_prefixes)


def call() -> int:
    '''
    Parse command line arguments to

        * list cloned git repositories,
        * add / remove git repositories
        * pull git repositories,
        * update (default),

    Returns:
        Error code to system

    '''
    env = ENV.update(cli_opts(CONFIG))

    if env.call_function == 'goodbye':
        de_init(CONFIG)
        return 0

    if env.call_function == 'init':
        err = init(CONFIG)
        if err:
            return err
        default_git_grp = GroupDB(path=CONFIG.data_dir, name='default')
        CONFIG.add(default_git_grp)
        CONFIG.store()
        default_git_grp.mk_structure()
        print("Close this shell (terminal) and open another session.")
        return 0

    if 'default' not in CONFIG.meta_db_dirs:
        # not initiated
        return 1

    if env.call_function == 'version':
        print(__version__, mark='info', pref='VERSION')
        return 0

    if env.call_function == 'meta':
        return print_prefixes(env=env)

    env_err = prepare_env(env)
    if env_err != 0:
        return env_err

    lock_state = lock(env=env, unlock=(env.call_function == 'unlock'))
    if lock_state != 0:
        return lock_state - 1

    if env.verbose:
        print(env, mark='bug')

    git_projects, failed_projects = find_gits(env=env)
    if env.call_function == 'info':
        lock(env=env, unlock=True)
        return print_projects(env=env, git_projects=git_projects,
                              failed_projects=failed_projects)

    queues = init_queues(env=env)
    try:
        if env.delete:
            git_projects = del_projects(env=env, git_projects=git_projects,
                                        queues=queues, del_list=env.delete)
        if env.install:
            add_projects(env=env, git_projects=git_projects,
                         queues=queues, to_add_list=env.install)
        if not env.stale:
            update_projects(env=env, git_projects=git_projects, queues=queues)
        for q_name in 'pull', 'clone':
            if q_name in queues:
                if env.verbose:
                    print(f'Wait: {queues[q_name].q_type} queue', mark='bug')
                os.waitpid(queues[q_name].pid, 0)
        for q_name in 'delete', 'install':
            if q_name in queues:
                try:
                    queues[q_name].done()
                except BrokenPipeError:
                    pass
        end_queues(env=env, queues=queues)
        lock(env=env, unlock=True)
        print()
        CONFIG.add({'path': env.prefix})
        CONFIG.prune()
        CONFIG.store()
        print('done.', mark=1)
    except KeyboardInterrupt:
        interrupt(queues)
        return 1
    return 0


if __name__ == '__main__':
    call()
