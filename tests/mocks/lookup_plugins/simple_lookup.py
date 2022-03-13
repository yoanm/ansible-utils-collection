# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible.module_utils.common.text.converters import to_native
from ansible_collections.yoanm.utils.plugins.lookup import LookupBase

# Hack to avoid loading "typing" module at runtime (issue with sanity tests on python 2.7) while keeping MyPy happy
MYPY = False
if MYPY:
    from typing import Dict, List


class LookupModule(LookupBase):
    def _run(self, terms, variables, **kwargs):
        # type: (LookupBase, List, Dict, **Dict) -> List
        res = dict(terms=terms, kwargs=kwargs)

        return [to_native(res)]
