# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Dict

from ansible_collections.yoanm.utils.plugins.action import ActionBase


class ActionModule(ActionBase):
    ARGUMENTS_SPEC = dict(
        name=dict(type='str', required=True),
        path=dict(type='str', default='default_path'),
    )

    def _run(self, task_vars, result):
        # type: (ActionModule, Dict, Dict) -> Dict
        result['simple_with_param_res'] = 'for a simple action with param'

        return result
