# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.common.text.converters import to_text
from ansible_collections.ansible.netcommon.plugins.sub_plugins.cli_parser.native_parser import CliParser

# Hack to avoid loading "typing" module at runtime (issue with sanity tests on python 2.7) while keeping MyPy happy
MYPY = False
if MYPY:
    from typing import Text, Optional, Dict, Any


def native_cli_parse(text, tmpl_path, task_vars=None, debug=False):
    # type: (Text, Text, Optional[Dict], bool) -> Dict[Text, Any]
    if task_vars is None:
        task_vars = dict()

    with open(tmpl_path, "rb") as file_handler:
        tmpl_contents = to_text(file_handler.read(), errors="surrogate_or_strict")
    parser = CliParser(task_args=dict(text=text), task_vars=task_vars, debug=debug)

    return parser.parse(template_contents=tmpl_contents)  # type: ignore
