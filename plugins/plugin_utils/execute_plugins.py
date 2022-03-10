# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from typing import Optional, Text, List, Dict, Any

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.plugins.loader import lookup_loader, action_loader
from ansible.plugins.lookup import LookupBase
from ansible.utils.unsafe_proxy import wrap_var


def execute_action(name, task_vars, loader_args=None, loader_kwargs=None):
    # type: (Text, Dict, Optional[List], Optional[Dict]) -> Dict
    if loader_kwargs is None:
        loader_kwargs = dict()
    if loader_args is None:
        loader_args = list()

    action = action_loader.get(name, *loader_args, **loader_kwargs)  # type: Optional[ActionBase]

    if action is None:
        raise AnsibleError('Unable to load action named "%s"' % name)

    return dict(action.run(task_vars=task_vars))


def execute_lookup(name, terms, lookup_vars, lookup_kwargs=None, loader_args=None, loader_kwargs=None):
    # type: (Text, List, Dict, Optional[Dict], Optional[List], Optional[Dict]) -> Any
    if lookup_kwargs is None:
        lookup_kwargs = dict()
    if loader_kwargs is None:
        loader_kwargs = dict()
    if loader_args is None:
        loader_args = list()

    lookup = lookup_loader.get(name, *loader_args, **loader_kwargs)  # type: Optional[LookupBase]

    if lookup is None:
        raise AnsibleError('Unable to load lookup named "%s"' % name)

    res = lookup.run(terms=terms, variables=lookup_vars, **lookup_kwargs)

    return wrap_var(res)
