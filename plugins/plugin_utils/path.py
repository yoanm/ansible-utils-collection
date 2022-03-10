# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os.path
from typing import Text, Optional, Dict, List

from ansible.plugins.loader import lookup_loader
from ansible.plugins.lookup import LookupBase
from ansible_collections.ansible.utils.plugins.module_utils.common.utils import to_list


def get_relative_collection_path():
    # type: () -> Text
    # Current file directory => __COLLECTION_PATH__/plugins/module_utils
    path = os.path.dirname(os.path.realpath(__file__))
    # Go up  => __COLLECTION_PATH__/plugins
    path = os.path.dirname(path)
    # Go up  => __COLLECTION_PATH__/
    path = os.path.dirname(path)

    return path


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


def append_collection_path_to_ansible_search_path(variables=None):
    # type: (Optional[Dict]) -> Dict
    variables = dict() if variables is None else variables
    if variables.get('ansible_search_path', None) is None:
        ansible_search_path = list()
    else:
        ansible_search_path = variables['ansible_search_path']

    collection_path = get_relative_collection_path()
    if collection_path not in ansible_search_path:
        ansible_search_path.append(collection_path)

    variables['ansible_search_path'] = ansible_search_path

    return variables
