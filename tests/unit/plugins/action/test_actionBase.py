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


class SimpleActionModule(unittest.TestCase):
    def setUp(self):
        task = MagicMock(Task)
        task.async_val = None  # Default being 0 but require the action to have _supports_async at True !
        task.action = "simple_action"
        task._role = None
        play_context = MagicMock()
        play_context.check_mode = False
        connection = MagicMock()
        fake_loader = DictDataLoader({})
        templar = Templar(loader=fake_loader)
        self._plugin = ConcreteActionModule(
            task=task,
            connection=connection,
            play_context=play_context,
            loader=fake_loader,
            templar=templar,
            shared_loader_obj=None,
        )

    def test_runnable(self):
        self._plugin._task.args = {}
        task_vars = {}
        expected_res = dict(changed=False, skipped=False, failed=False, my_result='a_result')

        self.assertDictEqual(self._plugin.run(tmp=None, task_vars=task_vars), expected_res)
