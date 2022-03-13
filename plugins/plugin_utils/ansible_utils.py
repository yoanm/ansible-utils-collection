# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible import __version__ as ansible_version

# Hack to avoid loading "typing" module at runtime (issue with sanity tests on python 2.7) while keeping MyPy happy
MYPY = False
if MYPY:
    from typing import Text, Tuple, List

_version_split = ansible_version.split('.')

VERSION_PART = (
    int(_version_split.pop(0)),
    int(_version_split.pop(0)),
    int(_version_split.pop(0)),
    [str(i) for i in _version_split]
)  # type: Tuple[int, int, int, List[Text]]

SHORT_VERSION = '.'.join([str(VERSION_PART[0]), str(VERSION_PART[1])])
SHORT_VERSION_FLOAT = float(SHORT_VERSION)
