#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This file is part of pspman.
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
Parse install-config files located at standard locations
to define installation methods.

Variables:
    code_path: str: path to source-code
    prefix: str: install-prefix
    build_dir: str: directory to build source for installation
    library: str: include libraries -L
    include: str: include libraries -I
    argv: list: argv to be passed during installation

Sequence of commands called:
    Installation: prefare, build, compile, install, whichever is not ``null``
    Uninstallation: build, uninstall, whichever is not ``null``

'''


import os
import shutil
from pathlib import Path
import yaml
import typing
from pspman.errors import (InstructError, InstructFmtError,
                           InstructTypeError, MissingInstructError)
from pspman.shell import process_comm
from pspman import CONFIG


class Instruct():
    '''
    Format handle of yaml file

    Arguments:
        indicate: list of file/dirnames that indicate the method
        exdicate: list of file/dirnames that prohibit the method
        requires: list of required dependencies to run the method
        env: dict of environment variables during (un)installation
        install: `ordered` list of ``steps`` for installation
        uninstall: `ordered` list of ``steps`` for uninstallation

            * steps: strings that may start with a caret sign (^)
              ^ indicates that this step is allowed to fail


    Args:
        instruct_file
    '''
    def __init__(self, instruct_file: Path = None):
        self.indicate: typing.List[str] = []
        self.exdicate: typing.List[str] = []
        self.requires: typing.List[str] = []
        self.env: typing.Dict[str, str] = {}
        self.install: typing.List[str] = []
        self.uninstall: typing.List[str] = []
        if instruct_file:
            self.read(instruct_file)

    def read(self, instruct_file: Path):
        '''
        Read instruction file and pass data for parsing

        Args:
            instruct_file: file path to <method>.yml

        '''
        try:
            with open(instruct_file, 'r') as instruct_h:
                instruct = yaml.safe_load(instruct_h)
            self.parse(instruct)
        except InstructError as err:
            raise InstructFmtError(instruct_file) from err

    def parse(self, instruct: dict):
        '''
        parse data from ``instruct`` yaml file
        Args:
            instruct: data out from yaml load

        Raises:
            InstructFmtError: bad format for install instructions
            MissingInstructError: essential instruction is missing
        '''
        self.indicate = instruct.get('indicate') or []
        if not isinstance(self.indicate, list):
            raise InstructTypeError('indicate', type(self.indicate), 'list')
        if self.indicate == []:
            raise MissingInstructError('indicate')
        self.exdicate = instruct.get('exdicate') or []
        if not isinstance(self.exdicate, list):
            raise InstructTypeError('exdicate', type(self.exdicate), 'list')
        self.requires = instruct.get('requires') or []
        if not isinstance(self.requires, list):
            raise InstructTypeError('requires', type(self.requires), 'list')
        self.env = instruct.get('env') or {}
        if not isinstance(self.env, dict):
            raise InstructTypeError('env', type(self.env), 'dict')
        self.install = instruct.get('install') or []
        if not isinstance(self.install, list):
            raise InstructTypeError('install', type(self.install), 'list')
        if self.install == []:
            raise MissingInstructError('install')
        self.uninstall = instruct.get('uninstall') or []
        if not isinstance(self.uninstall, list):
            raise InstructTypeError('uninstall', type(self.uninstall), 'list')

        # parse install
        for ids, step in enumerate(self.install):
            if not isinstance(step, str):
                raise InstructTypeError(f'step {ids}', type(step), 'str')


class DefInstruct():
    '''
    Instructions definition class

    Attributes:
        indicate: List[str]: files that help identfy the type of install
        commands: List[str]: commands essential for installation
        type: str: type of installation
        instruct: Dict[str, str]:
            * prepare: preparations instruction
            * build: build instruction
            * compile: compilation instruction
            * install: install instruction
            * uninstall: uninstall instruction
        env: dict: modified environment variables
        definition: Dict[str, Callable]:
            * prepare: preparations function
            * build: build function
            * compile: compilation function
            * install: install function
            * uninstall: uninstall function

    Args:
        instruct_file: yaml file describing instructions

    Raises:
        MissingInstructError: missing essential instruction
        InstructFmtError: Bad format of ``instruct_file``

    '''
    def __init__(self, instruct_file: Path):
        self.type = Path(instruct_file).name
        self.instruct = Instruct(instruct_file)
        self.i_steps: typing.List[typing.Callable] = []
        self.u_steps: typing.List[typing.Callable] = []
        for action in self.instruct.install:
            self.i_steps.append(self.instruct_def(action=action))

        for action in self.instruct.uninstall:
            self.u_steps.append(self.instruct_def(action=action))

    @staticmethod
    def _parse_i(instr: str = None,
                 argv: typing.Tuple[str, ...] = None,
                 libs: typing.Tuple[str, ...] = None,
                 incl: typing.Tuple[str, ...] = None) -> typing.List[str]:
        '''
        parse instruction string instr

        Args:
            instr: instruction string

        Returns:
            List of string separated by " "
        '''
        tuple_vars = {"__argv__": argv or (),
                      "__library__": libs or (),
                      "__include__": incl or ()}
        if instr is None:
            return []
        while "  " in instr:
            instr = instr.replace("  ", " ")
        cmd = instr.split(" ")
        for var, args in tuple_vars.items():
            if var not in cmd:
                continue
            var_idx = cmd.index(var)
            cmd.pop(var_idx)
            for element in args[::-1]:
                cmd.insert(var_idx, element)
        return cmd

    def instruct_def(self, action: str) -> typing.Callable:
        '''
        Generate a ``def`` (function) given an ``instructions`` Object

        Args:
            instructions

        Returns:
            Installation function constructed from action
        '''
        def act_f(code_path: Path,
                  prefix: Path,
                  build_dir: Path,
                  env: typing.Dict[str, str] = None,
                  argv: typing.Tuple[str, ...] = None) -> bool:
            '''
            function to prepare based on instructions

            Args:
                code_path: path to source code
                prefix: installtion prefix
                build_dir: build_directory
                env: custom env during installation
                argv: arguments to be supplied during installation

            Returns:
                success of compilation

            '''
            i_var_vals = {'__code_path__': str(code_path),
                          '__prefix__': str(prefix),
                          '__build_dir__': str(build_dir)}
            env = env or {}
            argv = argv or ()
            inc = prefix.joinpath('include')
            lib = prefix.joinpath('lib')
            incl = ("-I", str(inc)) if inc.is_dir() else ()
            libs = ("-L", str(lib)) if lib.is_dir() else ()
            env = {**self.instruct.env, **env}
            act_i = action
            ret_code = True if act_i[0] == '^' else False
            act_i = act_i.strip('^')
            for ivar, ival in i_var_vals.items():
                act_i = act_i.replace(ivar, ival)
                for key, val in env.items():
                    if val == ivar:
                        env[key] = ival
            comm = self._parse_i(instr=act_i, argv=argv, libs=libs, incl=incl)
            step_success = process_comm(*comm, env=env, fail_handle='report')
            return ret_code or bool(step_success)
        return act_f


def get_instruct(config: Path = None) -> typing.Dict[str, DefInstruct]:
    '''
    Scan standard locations for instruction files

    Args:
        custom_path: Scan this too
    '''
    standard_paths: typing.List[Path] = [
        Path(__file__).parent.joinpath('inst_config').resolve()
    ]
    if config is not None:
        if config.is_dir():
            standard_paths.append(config.resolve())
    known_types: typing.Dict[str, DefInstruct] = {}
    for inst_path in standard_paths:
        for node in inst_path.iterdir():
            if all((node.is_file(),
                    node.stem != 'template',
                    node.suffix == '.yml')):
                known_types[node.stem] = DefInstruct(node)
    return known_types


INST_METHODS = get_instruct(config=CONFIG.config_dir.joinpath('inst_config'))
'''
Methods of installation and uninstallation defined from instructions
Default: make, cmake, pip, meson/ninja
Extended for <instruct> by creating <config_dir>/inst_config/<instruct>.yml

'''


def run_install(i_type: str,
                code_path: Path,
                prefix=Path,
                argv: typing.List[str] = None,
                env: typing.Dict[str, str] = None) -> bool:
    '''
    (un)Install repository

    Args:
        code_path: path to source-code
        prefix: ``--prefix`` flag value to be supplied
        argv: Arguments to be supplied during (un)installation
        env: Modifications in shell env variables during (un)installation

    Returns:
        ``False`` if error/failure during (un)installation, else, ``True``

    '''
    uninstall = False
    if i_type not in INST_METHODS:
        i_type = i_type.replace("u_", '')
        uninstall = True
        if i_type not in INST_METHODS:
            return False
    argv = argv or []
    env = env or {}
    mod_env = os.environ.copy()
    for var, val in env.items():
        mod_env[var] = val
    build_dir = prefix.joinpath('temp_build', i_type)
    build_dir.mkdir(parents=True, exist_ok=True)
    steps = INST_METHODS[i_type].u_steps if uninstall \
        else INST_METHODS[i_type].i_steps
    for action in steps:
        if not action(
                code_path=code_path,
                prefix=prefix,
                env=mod_env,
                argv=argv,
                build_dir=build_dir
        ):
            shutil.rmtree(build_dir)
            return False
    shutil.rmtree(build_dir)
    return True
