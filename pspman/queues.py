#!/usr/bin/self.env python3
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
Command Queues

'''


import os
import sys
import typing
import multiprocessing
import time
import string
import socket
import threading
import random
import tempfile
import json
import yaml
from . import print
from .classes import InstallEnv, GitProject, GitProjectListEncoder
from .actions import delete, clone, update, install, success, failure
from .errors import ClosedQueueError
from .tag import TAG_ACTION


class PSPQueue:
    '''
    Base FIFO Queue object to push and retrieve tasks

    Attributes:
        env: installation context
        queue: queued ``GitProjects``
        downstream_qs: upstream queues feeding to this queue
            * success: successful projects are pushed here
            * fail: failed projects are pushed here
        upstream_qs: upstream queues feeding to this queue
        q_type: type of queue
        pid: pid of child process
        closed: Is the queue closed? (set by function ``done``)

    Args:
        env: installation context
        action: procedure to perform on each ``GitProject`` in the queue
        items:
        success_q: push to this queue, if action succeeds
        fail_q: push to this queue, if action fails
        **kwargs:
            * no-parallel: bool: True if single thread is to be used
            * items: Optional[Dict[str, GitProject]]: initialize with items
            * q_type: type of queue

    '''
    def __init__(self, env: InstallEnv,
                 action: typing.Callable,
                 fail_q: 'PSPQueue' = None,  # type: ignore
                 **kwargs):
        self.env = env
        self._running = False
        if kwargs.get('parallel') is not None:
            self._parallel = len(os.sched_getaffinity(0))
        else:
            self._parallel = 1
        self.upstream_qs: typing.List['PSPQueue'] = []  # type: ignore
        self.downstream_qs = {'success': kwargs.get('success'),
                              'fail': kwargs.get('fail')}
        for ds_q in self.downstream_qs.values():
            if ds_q is not None:
                ds_q.upstream_qs.append(self)
        self.action = action
        if kwargs.get('items') is None:
            self.queue: typing.Dict[str, GitProject] = {}
        else:
            self.queue = kwargs['items'].copy()
        self.q_type: str = kwargs.get('q_type', 'base')
        self._server, self._client = self._create_sockets()
        self._client.settimeout(10)
        self._server.settimeout(10)
        self.pid = self.start()
        self.closed = False

    def _create_sockets(self) -> typing.Tuple[socket.socket, socket.socket]:
        '''
        Parent: Create sockets
        '''
        name = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=10
        ))
        name = os.path.join(tempfile.gettempdir(), name +
                            f"_{self.q_type}_pspman.sock")
        # Child serves, parent process is the client
        server = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
        server.bind(name)
        server.listen()
        client = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM)
        client.connect(name)
        return server, client

    def add(self, project: GitProject) -> None:
        '''
        Parent: Add project to queue at the end

        Args:
            project: project to queue

        '''
        if not self._client._closed:  # type: ignore
            # send this to child
            self.copy_to_server(project)
        else:
            raise ClosedQueueError(self)

    def __len__(self) -> int:
        '''
        Parent/child: length of ojects in the queue

        '''
        return len(self.queue)

    def run_batch(self) -> None:
        '''
        Child: Execute threads that run ``action`` on all items in the queue

        '''
        if not len(self.queue):
            return
        self._running = True
        while len(self.queue):
            with multiprocessing.Pool(self._parallel) as pool:
                results: typing.List[typing.Tuple[str, int, bool]] = list(
                    pool.map_async(
                        self.action,
                        ((self.env, project) for project in
                         self.queue.values())).get()
                )
            for res in results:
                project = self.queue[res[0]]
                del self.queue[res[0]]
                project.tag = res[-2]
                if res[-1]:
                    self.on_success(project)
                else:
                    self.on_failure(project)
        self._running = False

    def on_success(self, project: GitProject):
        '''
        run on success
        '''
        if self.downstream_qs['success'] is not None:
            self.downstream_qs['success'].add(project)

    def on_failure(self, project: GitProject):
        '''
        run on failure
        '''
        if self.downstream_qs['fail'] is not None:
            self.downstream_qs['fail'].add(project)

    def done(self, caller: 'PSPQueue' = None) -> None:  # type: ignore
        '''
        Parent: No more items will be added.
        Finish current list and exit

        '''
        if caller is not None:
            self.upstream_qs.pop(self.upstream_qs.index(caller))
            if len(self.upstream_qs) != 0:
                return
        if self.env.verbose:
            print(f"Closing Queue {self.q_type}", mark='bug')
        self._client.send((0).to_bytes(length=64, byteorder='big'))
        self.closed = True

    def start(self) -> int:
        '''
        Parent: Start a batch run

        Returns:
            child: 0
            parent: >0

        '''
        pid = os.fork()
        if pid == 0:
            # child server
            pipe, _ = self._server.accept()
            while not self._server._closed:  # type: ignore
                # socket is not closed
                if self._running:
                    # Wait for job to complete
                    print('Server child is running...', mark='bug')
                    time.sleep(10)
                else:
                    # Action is not running
                    self.handle_conn(pipe)
                    # Batch run, ready to receive next signal
            else:
                # final pass
                self.run_batch()
                if self.downstream_qs['success'] is not None:
                        self.downstream_qs['success'].done(self)
                if self.downstream_qs['fail'] is not None:
                        self.downstream_qs['fail'].done(self)
            sys.exit(0)
        else:
            # parent client
            pass
        return pid

    def handle_conn(self, pipe: socket.socket) -> None:
        '''
        Child: handle each parent connection
        '''
        close = self.copy_from_client(pipe)
        self.run_batch()
        if close and not self._server._closed:  # type: ignore
            self._server.close()

    def copy_from_client(self, pipe: socket.socket) -> bool:
        '''
        Child: copy parent's queue

        Returns:
            ``True`` if 'close' instruction is received

        '''
        try:
            size_in_bytes = pipe.recv(64)
            chunk = int.from_bytes(bytes=size_in_bytes, byteorder='big')
            if chunk == 0:
                # input closed
                return True
            self.queue = {name: GitProject(data=project_data)
                          for name, project_data in
                          json.loads(pipe.recv(chunk).decode('utf-8')).items()}
        except socket.timeout:
            print('Client parent did\'t respond...', mark='bug')
            time.sleep(10)
        return False

    def copy_to_server(self, project: GitProject = None):
        '''
        Parent: copy to child's queue

        '''
        # FAIL: All getting pushed, and only first is received
        if project:
            self.queue[project.name] = project
        try:
            to_json = json.dumps(
                self.queue,
                cls=GitProjectListEncoder
            ).encode('utf-8')
            self._client.send(len(to_json).to_bytes(length=64,
                                                    byteorder='big'))
            self._client.send(to_json)
            self.queue = {}
        except socket.timeout:
            print('Server child did\'t respond...', mark='info')

    def __repr__(self) ->str:
        '''
        Representation of queue

        '''
        represent: typing.List[str] = [f'Queue: {self.q_type}']
        represent.append(
            f"Queue-success: {self.downstream_qs['success'].q_type}"
            if self.downstream_qs['success'] is not None
            else 'Queue-success: ``None``'
        )
        represent.append(f"Queue-fail: {self.downstream_qs['fail'].q_type}"
                         if self.downstream_qs['fail'] is not None
                         else 'Queue-fail: ``None``')
        represent.append("Upstream feeds:")
        for up_q in self.upstream_qs:
            represent.append(f"\t{up_q.q_type}")
        represent.append(f'contents: {len(self)} items')
        return '\n'.join(represent)


class FailQueue(PSPQueue):

    '''
    Queue to reguster Successful objects
    '''
    def __init__(self, env: InstallEnv, **kwargs):
        super().__init__(env=env, action=failure, q_type='fail', **kwargs)


class TermQueue(PSPQueue):
    '''
    Terminal queues that do not have a downstream action queue

    Attributes:
        registry: Log held by child process about action success/failure

    '''
    def __init__(self, env: InstallEnv, action: typing.Callable,
                 q_type: str = 'terminal', **kwargs):
        super().__init__(env=env, action=action, q_type=q_type, **kwargs)
        self.registry: typing.List[GitProject] = []

    def on_success(self, project: GitProject):
        '''
        Child: store GitProject state
        '''
        with open(os.path.join(self.env.clone_dir,
                               '.pspman.healthy.yml'), 'a') as db_handle:
            yaml.dump({project.name: project.__dict__}, db_handle)

    def on_failure(self, project: GitProject):
        '''
        Child: store GitProject state
        '''
        with open(os.path.join(self.env.clone_dir,
                               '.pspman.fail.yml'), 'a') as db_handle:
            yaml.dump({project.name: project.__dict__}, db_handle)


class SuccessQueue(TermQueue):

    '''
    Queue to reguster Successful objects

    '''
    def __init__(self, env: InstallEnv, **kwargs):
        super().__init__(env=env, action=success, q_type='success', **kwargs)


class DeleteQueue(TermQueue):
    '''
    Queue for projects to delete
    '''
    def __init__(self, env: InstallEnv,
                 success: PSPQueue, fail: PSPQueue, **kwargs):
        super().__init__(env=env, action=delete, q_type='delete',
                         success=success, fail=fail, **kwargs)

    def on_success(self, project: GitProject):
        '''
        run on success
        '''
        if self.downstream_qs['success'] is not None:
            self.downstream_qs['success'].add(None)

class InstallQueue(PSPQueue):
    '''
    Queue of projects to install
    '''
    def __init__(self, env: InstallEnv, success: PSPQueue,
                 fail: PSPQueue, **kwargs):
        super().__init__(env=env, action=install, q_type='install',
                         success=success, fail=fail, **kwargs)


class PullQueue(PSPQueue):
    '''
    Queue of source codes to pull
    '''
    def __init__(self, env: InstallEnv, success: PSPQueue,
                 fail: PSPQueue, **kwargs):
        super().__init__(env=env, action=update, q_type='pull',
                         success=success, fail=fail, **kwargs)

    def on_success(self, project: GitProject):
        '''
        run on success
        '''
        project.mark_update_time()
        if self.downstream_qs['success'] is not None:
            self.downstream_qs['success'].add(project)


class CloneQueue(PSPQueue):
    '''
    Queue of projects to clone
    '''
    def __init__(self, env: InstallEnv, success: PSPQueue,
                 fail: PSPQueue, **kwargs):
        super().__init__(env=env, action=clone, q_type='clone',
                         success=success, fail=fail, **kwargs)

    def on_success(self, project: GitProject):
        '''
        run on success
        '''
        project.mark_update_time()
        if self.downstream_qs['success'] is not None:
            self.downstream_qs['success'].add(project)
