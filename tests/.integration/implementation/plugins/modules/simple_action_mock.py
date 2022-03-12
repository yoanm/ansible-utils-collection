# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: simple_action_mock
version_added: 0.1.0
short_description: Format and write a zone configuration for bind9
description:
  - Module takes a zone configuration object
author:
    - Yoanm (@yoanm)
extends_documentation_fragment:
    - action_common_attributes
    - action_common_attributes.conn
    - action_common_attributes.facts
options:
  name:
    description:
    - Zone name
    type: str
    required: yes
  path:
    description:
    - Zone file path on the remote node
    type: path
    required: yes
  zone:
    description:
    - Zone configuration object
    type: dict
    required: yes
  on_change_update_serial:
    description:
    - Update the existing zone serial in case the new content is different. Default True
    type: bool
    default: yes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: full
    become:
        support: full
    delegation:
        support: full
    connection:
        support: full
    facts:
        support: full
    platform:
        platforms: debian
'''

EXAMPLES = r'''
- name: TODO TODO TODO TODO TODO TODO
  simple_action_mock:
'''

RETURN = r'''
new_serial:
    description: Command line executed
    type: str
    returned: changed
    sample: 2022022803
zone_file_content:
    description: Zone file content
    type: str
    returned: always
'''
