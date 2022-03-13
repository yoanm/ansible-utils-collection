# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Dict

from ansible.errors import AnsibleActionFail
from ansible.module_utils.common.text.converters import to_native, to_bytes
from ansible_collections.yoanm.utils.tests.mocks.action_plugins.simple_action import (
    ActionModule as BaseActionModule
)


class ActionModule(BaseActionModule):
    ARGUMENTS_SPEC = dict(
        generate_local_tmpfile=dict(type='bool', default=False),
        local_tmpfile_content=dict(type='raw', default=None),
        fetch_remote_file=dict(type='bool', default=False),
        remote_file_path=dict(type='path', default=None),
        mirror_remote_file=dict(type='bool', default=False),
        mirror_source_path=dict(type='path', default=None),
    )

    CONDITIONAL_ARGUMENTS_SPEC = dict(
        mutually_exclusive=(
            ['generate_local_tmpfile', 'fetch_remote_file', 'mirror_remote_file'],
            ['local_tmpfile_content', 'remote_file_path', 'mirror_source_path'],
        ),
        required_if=[
            ['generate_local_tmpfile', True, ['local_tmpfile_content']],
            ['fetch_remote_file', True, ['remote_file_path']],
            ['mirror_remote_file', True, ['mirror_source_path']],
        ],
        required_one_of=['generate_local_tmpfile', 'fetch_remote_file', 'mirror_remote_file']
    )

    def _run(self, task_vars, result):
        # type: (ActionModule, Dict, Dict) -> Dict

        if self._validated_args.get('generate_local_tmpfile', None):
            self._display.display('Generate local tmpfile')
            result['file_path'] = self._create_local_tempfile(to_bytes(self._validated_args.get('local_tmpfile_content')))
        elif self._validated_args.get('fetch_remote_file', None):
            self._display.display('Fetch remote file')
            result['file_path'] = self._fetch_remote_file_to_local_tmp(
                to_native(self._validated_args.get('remote_file_path')),
                self._validated_args
            )
        elif self._validated_args.get('mirror_remote_file', None):
            self._display.display('Mirror remote file')
            result['file_path'] = tmp_file_path = self._generate_remote_tmp_file_path()
            self._mirror_remote_file(
                to_native(self._validated_args.get('mirror_source_path')),
                tmp_file_path
            )

        return result
