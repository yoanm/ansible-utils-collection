# -*- coding: utf-8 -*-
# (c) 2020-2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
        self.fake_loader = DictDataLoader({})
        self.templar = Templar(loader=self.fake_loader)

    def _init_plugin(self, plugin_cls=ConcreteActionModule):
        self._plugin = plugin_cls(
            task=self.task,
            connection=self.connection,
            play_context=self.play_context,
            loader=self.fake_loader,
            templar=self.templar,
            shared_loader_obj=None,
        )

    def test_base_runnable(self):
        self._init_plugin()
        self._plugin._task.args = dict()
        task_vars = dict()
        expected_res = dict(changed=False, skipped=False, failed=False, my_result='a_result')
        actual_res = self._plugin.run(tmp=None, task_vars=task_vars)
        actual_res_sanitized = dict({key: actual_res[key] for key in expected_res.keys() if key in actual_res})

        self.assertDictEqual(actual_res_sanitized, expected_res)

    def test_doc_validation(self):
        self._init_plugin(ConcreteActionModuleWithDoc)
        self._plugin._task.args = dict()
        task_vars = dict()
        self.maxDiff = None
        expected_res = dict(failed=True, errors=['missing required arguments: name'])
        actual_res = self._plugin.run(tmp=None, task_vars=task_vars)
        actual_res_sanitized = dict({key: actual_res[key] for key in expected_res.keys() if key in actual_res})

        self.assertDictEqual(actual_res_sanitized, expected_res)

    def test_argspec_validation(self):
        self._init_plugin(ConcreteActionModuleWithArgSpec)
        self._plugin._task.args = dict()
        task_vars = dict()
        self.maxDiff = None
        expected_res = dict(failed=True, errors=['missing required arguments: name'])
        actual_res = self._plugin.run(tmp=None, task_vars=task_vars)
        actual_res_sanitized = dict({key: actual_res[key] for key in expected_res.keys() if key in actual_res})

        self.assertDictEqual(actual_res_sanitized, expected_res)


if __name__ == '__main__':
    unittest.main()
