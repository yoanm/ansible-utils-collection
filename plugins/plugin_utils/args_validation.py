# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible_collections.ansible.utils.plugins.module_utils.common.argspec_validate import AnsibleArgSpecValidator

# Hack to avoid loading "typing" module at runtime (issue with sanity tests on python 2.7) while keeping MyPy happy
MYPY = False
if MYPY:
    from typing import Tuple, Union, Optional, Dict, List, Text, TypeVar

    class PluginArgSpecReturnRes(Dict):
        failed: bool
        errors: List[Text]
        msg: Optional[Text]

    PluginArgSpecReturnResType = TypeVar('PluginArgSpecReturnResType', bound=PluginArgSpecReturnRes)
    PluginArgSpecReturn = Tuple[PluginArgSpecReturnResType, Dict]
    ArgSpecReturn = Tuple[bool, List[Text], Dict]

    ArgSpecSchema = Union[Dict, Text]
    ArgSpecOptionalSchema = Optional[Dict]


def check_argspec(name, args, schema, schema_format="doc", schema_conditionals=None, other_args=None):
    # type: (Text, Dict, ArgSpecSchema, Text, ArgSpecOptionalSchema, ArgSpecOptionalSchema) -> ArgSpecReturn
    """
    Same as the original C(check_argspec) but with typehint
    +always returns a list of errors (from original function it may be a list of string or a string)
    +always returns a dict for updated_params (enclear from original implementation)
    """
    aav = AnsibleArgSpecValidator(
        data=args,
        schema=schema,
        schema_format=schema_format,
        schema_conditionals=schema_conditionals,
        other_args=other_args,
        name=name,
    )

    valid, errors, updated_params = aav.validate()

    # Always return a list of error string
    if not valid and not isinstance(errors, list):
        errors = [errors]
    else:
        errors = []

    # Always return a dict for updated_params
    if not isinstance(updated_params, dict):
        updated_params = dict()

    return valid, errors, updated_params


def check_plugin_argspec(plugin_name, plugin_args, schema, schema_format="doc", schema_conditionals=None, other_args=None):
    # type: (Text, Dict, ArgSpecSchema, Text, ArgSpecOptionalSchema, ArgSpecOptionalSchema) -> PluginArgSpecReturn
    """
    Same as the original C(check_argspec) but with typehint (and removal of useless 'valid' property)
    +add 'other_args' param
    +always returns a list of errors (from original function it may be a list of string or a string)
    +always returns a dict for updated_params (enclear from original implementation)
    """
    valid, errors, updated_params = check_argspec(
        name=plugin_name,
        schema=schema,
        schema_format=schema_format,
        schema_conditionals=schema_conditionals,
        args=plugin_args,
        other_args=other_args
    )
    # Ensure default values
    check_res = {'errors': [], 'failed': (not valid)}
    if not valid:
        check_res["errors"] = errors if isinstance(errors, list) else [errors]
        check_res["msg"] = "Errors during argspec validation for %s plugin" % plugin_name

    # Always return a list of error string
    if not valid:
        if 'errors' in check_res and check_res['errors'] is not None and not isinstance(check_res['errors'], list):
            check_res['errors'] = [check_res['errors']]

    return check_res, updated_params
