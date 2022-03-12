# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Dict

from ansible_collections.yoanm.utils.plugins.action import ActionBase


class ActionModule(ActionBase):
    def _run(self, task_vars, result):
        # type: (ActionModule, Dict, Dict) -> Dict

        return result
