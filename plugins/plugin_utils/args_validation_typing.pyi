# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

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
