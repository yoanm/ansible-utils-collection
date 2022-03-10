# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Tuple, Union, Optional, Dict, List, Text

from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import AnsibleArgSpecValidator

ValidateArgsResult = Tuple[bool, List, Dict]
ValidateArgsSchema = Union[Dict, Text]
ValidateArgsSchemaConditionals = Optional[Dict]


def validate_args(caller, args, schema, schema_format='doc', schema_conditionals=None):
    # type: (Text, Dict, ValidateArgsSchema, Text, ValidateArgsSchemaConditionals) -> ValidateArgsResult
    aav = AnsibleArgSpecValidator(
        data=args,
        schema=schema,
        schema_format=schema_format,
        schema_conditionals=schema_conditionals,
        name=caller
    )

    return aav.validate()  # type: ignore
