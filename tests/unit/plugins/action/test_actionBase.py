# -*- coding: utf-8 -*-
# (c) 2020-2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os.path
from random import getrandbits
from typing import Type

from ansible.playbook.task import Task
from ansible.template import Templar

from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import MagicMock
from ansible_collections.community.internal_test_tools.tests.unit.mock.loader import DictDataLoader
from ansible_collections.yoanm.utils.plugins.action import ActionBase


class ConcreteActionModule(ActionBase):
    def _run(self, task_vars, result):
        result['my_result'] = 'a_result'
        return result


class ConcreteActionModuleWithDoc(ConcreteActionModule):
    DOCUMENTATION = r'''
---
options:
  name:
    description:
    - A name
    type: str
    required: yes
  path:
    description:
    - A path
    type: string
    required: no
'''


class ConcreteActionModuleWithArgSpec(ConcreteActionModule):
    ARGUMENTS_SPEC = BINARY_ARGS_SPEC = dict(
        name=dict(type='str', required=True),
        path=dict(type='str'),
    )


class SimpleActionModule(unittest.TestCase):
    def setUp(self):
        self.task = MagicMock(Task)
        self.task.async_val = None  # Default being 0 but require the action to have _supports_async at True !
        self.task.action = "simple_action"
        self.task._role = None
        self.play_context = MagicMock()
        self.play_context.check_mode = False
        self.connection = MagicMock()
        self.connection._shell = MagicMock()
        self.fake_loader = DictDataLoader({})
        self.templar = Templar(loader=self.fake_loader)

    def _init_plugin(self, plugin_cls=ConcreteActionModule):
        # type: (Type[ConcreteActionModule]) -> ConcreteActionModule
        plugin = plugin_cls(
            task=self.task,
            connection=self.connection,
            play_context=self.play_context,
            loader=self.fake_loader,
            templar=self.templar,
            shared_loader_obj=None,
        )
        plugin._task.async_val = None
        plugin._task.args = dict()

        return plugin

    def test_base_runnable(self):
        plugin = self._init_plugin()

        expected_res = dict(changed=False, skipped=False, failed=False, my_result='a_result')
        actual_res = plugin.run()
        actual_res_sanitized = dict()
        for key in expected_res.keys():
            if key in actual_res:
                actual_res_sanitized[key] = actual_res[key]

        self.assertDictEqual(actual_res_sanitized, expected_res)

    def test_doc_validation(self):
        plugin = self._init_plugin(ConcreteActionModuleWithDoc)

        expected_res = dict(failed=True, errors=['missing required arguments: name'])
        actual_res = plugin.run()
        actual_res_sanitized = dict()
        for key in expected_res.keys():
            if key in actual_res:
                actual_res_sanitized[key] = actual_res[key]

        self.assertDictEqual(actual_res_sanitized, expected_res)

    def test_argspec_validation(self):
        plugin = self._init_plugin(ConcreteActionModuleWithArgSpec)

        expected_res = dict(failed=True, errors=['missing required arguments: name'])
        actual_res = plugin.run()
        actual_res_sanitized = dict()
        for key in expected_res.keys():
            if key in actual_res:
                actual_res_sanitized[key] = actual_res[key]

        self.assertDictEqual(actual_res_sanitized, expected_res)

    def test_find_needle_in_collection_method(self):
        plugin = self._init_plugin(ConcreteActionModuleWithArgSpec)

        actual_res = plugin._find_needle_in_collection('ansible_collections.yoanm.utils', 'plugins', 'README.md')
        expected_res = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../../../plugins/README.md'))

        self.assertEqual(actual_res, expected_res)

    def test_generate_tmp_filename_method(self):
        plugin = self._init_plugin(ConcreteActionModuleWithArgSpec)

        actual_res = [plugin._generate_tmp_filename() for i in range(0, 3)]
        # Remove doubles
        actual_res_sanitized = list(dict.fromkeys(actual_res))

        self.assertEqual(actual_res.sort(), actual_res_sanitized.sort())

    def test_create_local_tempfile_method(self):
        self.skipTest('TODO !')
        plugin = self._init_plugin(ConcreteActionModuleWithArgSpec)
        my_content = bytes(getrandbits(32))

        def side_effect(arg):
            if arg == 'system_tmpdirs':
                return ['/tmp']
            raise Exception('Unexpected method call get_options(%s)' % repr(arg))

        plugin._connection._shell.get_options.side_effect = side_effect

        file_path = plugin._create_local_tempfile(my_content)

        with open(file_path) as f:
            self.assertEqual(f.read(), my_content)
