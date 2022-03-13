# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Dict

from ansible_collections.yoanm.utils.tests.mocks.action_plugins.simple_action import (
    ActionModule as BaseActionModule
)


class ActionModule(BaseActionModule):
    def _run(self, task_vars, result):
        # type: (ActionModule, Dict, Dict) -> Dict
        raise Exception('Argh !')
