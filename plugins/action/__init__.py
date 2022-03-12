# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import base64
import os.path
from abc import abstractmethod
from random import getrandbits

from ansible.errors import AnsibleActionFail
from ansible.module_utils.common.dict_transformations import dict_merge
from ansible.module_utils.common.text.converters import to_native
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play_context import PlayContext
from ansible.playbook.task import Task
from ansible.plugins.action import ActionBase as AnsibleActionBase
from ansible.plugins.connection import ConnectionBase
from ansible.template import Templar
from ansible.utils.display import Display

from ..plugin_utils.args_validation import check_plugin_argspec
from ..plugin_utils.execute_plugins import execute_action, execute_lookup
from ..plugin_utils.path import get_collection_path

# Hack to avoid loading "typing" module at runtime (issue with sanity tests on python 2.7) while keeping MyPy happy
MYPY = False
if MYPY:
    from typing import Text, Optional, Dict, Any, List
    from ..plugin_utils import args_validation as args_typing


class ActionBase(AnsibleActionBase):
    _task = None  # type: Task
    _connection = None  # type: ConnectionBase
    _play_context = None  # type: PlayContext
    _loader = None  # type: DataLoader
    _templar = None  # type: Templar
    _shared_loader_obj = None  # type: Any
    _display = None  # type: Display

    # def __init__(self, task: Task, connection: ConnectionBase, play_context: PlayContext, loader: DataLoader,
    #              templar: Templar, shared_loader_obj: Any):
    #     super(ActionBase, self).__init__(task, connection, play_context, loader, templar, shared_loader_obj)

    def run(self, tmp=None, task_vars=None):
        # type:(ActionBase, Any, Optional[Dict]) -> Dict
        if task_vars is None:
            task_vars = dict()

        result = super(ActionBase, self).run(tmp, task_vars)  # type: Dict
        result.update(dict(changed=False, skipped=False, failed=False))

        # Validated args specification
        self.__validate_args(result)

        # Early return in case there is already a failure
        if result.get('failed'):
            return result

        # Execute internal method
        # try:
        return self._run(task_vars=task_vars, result=result)
        # except Exception as exc:
        #    self._display.error('Error occurred during action execution: %s' % exc)
        #    result['failed'] = True
        #    result['error'] = to_text(exc)
        #    result['exception'] = traceback.format_exc()

        # return result

    @abstractmethod
    def _run(self, task_vars, result):
        # type: (ActionBase, Dict, Dict) -> Dict
        """ Action Plugins should implement this method to perform their own business
        Method will be safely executed by C(ActionBase::run)
        """

    def check_argspec(
        self,  # type: ActionBase
        args,  # type: Dict
        schema,  # type: args_typing.ArgSpecSchema
        schema_format='doc',  # type: Text
        schema_conditionals=None,  # type: args_typing.ArgSpecOptionalSchema
        other_args=None  # type: args_typing.ArgSpecOptionalSchema
    ):
        # type: (...) -> args_typing.PluginArgSpecReturn
        return check_plugin_argspec(self._task.get_name(), args, schema, schema_format, schema_conditionals, other_args)

    def _execute_module(self,  # type: ActionBase
                        module_name=None,  # type: Optional[Text]
                        module_args=None,  # type: Optional[Dict]
                        tmp=None,  # type: Optional[Any]
                        task_vars=None,  # type: Optional[Dict]
                        persist_files=False,  # type: Optional[bool]
                        delete_remote_tmp=None,  # type: Optional[bool]
                        wrap_async=False,  # type: Optional[bool]
                        result=None  # type: Optional[Dict]
                        ):
        # type: (...) -> Dict
        module_res = super(ActionBase, self)._execute_module(
            module_name=module_name,
            module_args=module_args,
            task_vars=task_vars,
            tmp=tmp,
            persist_files=persist_files,
            delete_remote_tmp=delete_remote_tmp,
            wrap_async=wrap_async
        )  # type: Dict

        # Merge result to existing result if provided
        if result is not None:
            is_action_module = module_name is None or module_name == self._task.get_name()
            real_module_name = self._task.get_name() if is_action_module else module_name
            result.update({real_module_name: module_res})
            # Pop values to avoid having them two times
            for var in ['diff', 'changed', 'failed', 'ansible_facts', 'error', 'errors', 'exception', 'invocation']:
                if module_res.get(var, None) is not None:
                    new_value = module_res.pop(var)
                    if isinstance(result.get(var, None), dict):
                        result[var] = dict_merge(result[var], new_value)
                    elif var in ['exception', 'error', 'errors'] and var in result:
                        result[var] = result[var] + new_value
                    else:
                        result[var] = new_value

        return module_res

    def _execute_action(self, name, args, task_vars):
        # type: (ActionBase, Text, Dict, Dict) -> Dict
        """
        :return: dict
        """
        task_copy = self._task.copy()
        task_copy.args = args

        loader_kwargs = dict(
            task=task_copy,
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj
        )

        return execute_action(name, task_vars=task_vars, loader_kwargs=loader_kwargs)

    def _execute_lookup(self, name, terms, variables, **kwargs):
        # type: (ActionBase, Text, List, Dict, **Dict) -> Any
        loader_kwargs = dict(loader=self._loader, templar=self._templar)
        lookup_vars = self._task.args.copy()
        lookup_vars.update(variables)

        return execute_lookup(name, terms=terms, lookup_vars=lookup_vars, lookup_kwargs=kwargs,
                              loader_kwargs=loader_kwargs)

    def _find_needle_in_collection(self, c_full_name, dirname, needle, collection_first=False):
        # type: (ActionBase, Text, Text, Text, bool) -> Text
        """
            find a needle inside "{c_full_name}" ansible collection directory
        """

        if collection_first:
            path_stack = get_collection_path(c_full_name) + self._task.get_search_path()
        else:
            path_stack = self._task.get_search_path() + get_collection_path(c_full_name)

        self._display.vvv('Try to find %s or %s under %s ' % (os.path.join(dirname, needle), needle, path_stack))
        # If nothing found, it will throw an exception
        return self._loader.path_dwim_relative_stack(path_stack, dirname, needle)  # type: ignore

    def __validate_args(self, result):
        # type: (ActionBase, Dict) -> None
        doc = getattr(self, "DOCUMENTATION", None)
        if doc is not None:
            check_res, self._task.args = self.check_argspec(args=self._task.args, schema=doc)
            if not check_res['failed']:
                result.update(check_res)
        else:
            args_spec = getattr(self, "ARGUMENTS_SPEC", None)
            if args_spec is not None:
                self._display.display('args_spec=%s' % args_spec)
                check_res, self._task.args = self.check_argspec(args=self._task.args,
                                                                schema=dict(argument_spec=args_spec),
                                                                schema_format='argspec')
                if not check_res['failed']:
                    result.update(check_res)

    def _mirror_remote_file(self, source, dest):
        # type: (ActionBase, Text, Text) -> None
        """
        Warning: Method doesn't manage check mode, file will always be created, you are responsible for removing it !
        """
        self._display.v('Mirror remote file %s to %s' % (source, dest))
        # Use '-a' to preserve permissions, ownership, SELinux stuff, etc
        cmd = ' '.join(['cp', '-a', self._connection._shell.quote(source), self._connection._shell.quote(dest)])
        result = self._low_level_execute_command(cmd)
        if result.get('rc', None) != 0:
            raise AnsibleActionFail('Error during remote file mirroring: %s' % result)

    def _fetch_remote_file_to_local_tmp(self, task_vars, remote_source):
        # type: (ActionBase, Dict, Text) -> Text
        """
        :param task_vars:
        :param remote_source: Remote source file path
        :return: Local file path
        """
        self._display.v('Fetch remote file %s to local tmp directory' % remote_source)
        res = self._execute_module(
            module_name='ansible.legacy.slurp',
            module_args=dict(path=remote_source),
            task_vars=task_vars
        )
        if res.get('failed', False):
            raise AnsibleActionFail('Error during remote file mirroring: %s' % to_native(res))

        content = b''
        if 'content' in res:
            if res['encoding'] == u'base64':
                content = base64.b64decode(res['content'])
            else:
                raise AnsibleActionFail(
                    'Error during remote file mirroring, unknown encoding: %s' % to_native(res['encoding']))

        return self._create_local_tempfile(content)

    def _create_local_tempfile(self, content):
        # type: (ActionBase, bytes) -> Text
        """
        Create a tmp file located on local temporary directory

        :param content: File content
        :return: local tmp file path
        """
        tmp_file_path = self._generate_local_tmp_file_path()
        try:
            with open(tmp_file_path, "xb") as file_handler:
                file_handler.write(content)
                file_handler.close()
        except Exception as err:
            os.remove(tmp_file_path)
            raise AnsibleActionFail(err)

        return tmp_file_path

    def _generate_tmp_filename(self):
        # type: (ActionBase) -> Text
        """
        Generate a unique filename based on current task name and time

        :return: filename
        """
        return str(self._task.get_name()) + '-' + str(getrandbits(32)) + '.tmp'

    def _generate_remote_tmp_file_path(self):
        # type: (ActionBase) -> Text
        if self._connection._shell.tmpdir is None:
            tmp_dir = self._make_tmp_path()  # Initialize tmp directory
        else:
            tmp_dir = self._connection._shell.tmpdir

        return os.path.join(tmp_dir, self._generate_tmp_filename())

    def _generate_local_tmp_file_path(self):
        # type: (ActionBase) -> Text
        return os.path.join(self.get_shell_option('system_tmpdirs')[0], self._generate_tmp_filename())
