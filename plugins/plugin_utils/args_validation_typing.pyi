# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Tuple, Union, Optional, Dict, List, Text, TypeVar, Type, TypedDict


class PluginArgSpecReturnRes(TypedDict):
    failed: bool
    errors: List[Text]
    msg: Optional[Text]

PluginArgSpecReturn = Tuple[PluginArgSpecReturnRes, Dict]
ArgSpecReturn = Tuple[bool, List[Text], Dict]

ArgSpecSchema = Union[Dict, Text]
ArgSpecOptionalSchema = Optional[Dict]
