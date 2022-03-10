# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os.path

from ansible.plugins.loader import lookup_loader
from ansible.plugins.lookup import LookupBase
from ansible_collections.ansible.utils.plugins.module_utils.common.utils import to_list

# Hack to avoid loading "typing" module at runtime (issue with sanity tests on python 2.7) while keeping MyPy happy
MYPY = False
if MYPY:
    from typing import Text, Optional, Dict, List


def get_collection_path(c_full_name):
    # type: (Text) -> List[Text]
    lookup = lookup_loader.get('config')  # type: Optional[LookupBase]

    if lookup is None:
        raise Exception('Unable to load config lookup !')

    paths = to_list(to_list(lookup.run(terms=['COLLECTIONS_PATHS']))[0])

    res = []
    for path in paths:
        res.append(os.path.join(path, *c_full_name.split('.')))

    return res


def append_collection_path_to_ansible_search_path(c_full_name, variables=None):
    # type: (Text, Optional[Dict]) -> Dict
    variables = dict() if variables is None else variables
    if variables.get('ansible_search_path', None) is None:
        ansible_search_path = list()
    else:
        ansible_search_path = variables['ansible_search_path']

    collection_path_list = get_collection_path(c_full_name)
    for collection_path in collection_path_list:
        if collection_path not in ansible_search_path:
            ansible_search_path.append(collection_path)

    variables['ansible_search_path'] = ansible_search_path

    return variables
