# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible import __version__ as ansible_version
import re

# Hack to avoid loading "typing" module at runtime (issue with sanity tests on python 2.7) while keeping MyPy happy
MYPY = False
if MYPY:
    from typing import Text, Tuple, List

_version_split = ansible_version.split('.')

VERSION_PART = list()  # type: List[str]

for part in _version_split:
    try:
        VERSION_PART.append(str(int(part)))
    except ValueError:  # part may contain non-numeric chars (like 'rc1')
        matches = re.match(r'^(\d+)(.*)\.$', part)
        if matches is not None and matches.groups() is not None:
            groups = list(matches.groups())  # type: List
            if len(groups) > 1: # There is numeric chars at beginning
                VERSION_PART.append(str(int(groups.pop(0))))
            VERSION_PART.append(str(groups.pop(0)))
        else:
            VERSION_PART.append(str(part))

SHORT_VERSION = '.'.join([str(VERSION_PART[0]), str(VERSION_PART[1])])
SHORT_VERSION_FLOAT = float(SHORT_VERSION)
