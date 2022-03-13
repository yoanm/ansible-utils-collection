# -*- coding: utf-8 -*-
# (c) 2020-2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from typing import Type
from ansible.template import Templar

from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.mock.loader import DictDataLoader
from ansible_collections.yoanm.utils.plugins.lookup import LookupBase


class ConcreteLookup(LookupBase):
    def _run(self, terms, variables, **kwargs):
        return ['my_result']


class SimpleLookup(unittest.TestCase):
    def setUp(self):
        self.fake_loader = DictDataLoader({})
        self.templar = Templar(loader=self.fake_loader)

    def _init_plugin(self, plugin_cls=ConcreteLookup):
        # type: (Type[ConcreteLookup]) -> ConcreteLookup
        plugin = plugin_cls(
            loader=self.fake_loader,
            templar=self.templar,
        )

        return plugin

    def test_base_runnable(self):
        plugin = self._init_plugin()

        expected_res = ['my_result']
        actual_res = plugin.run([])

        self.assertListEqual(actual_res, expected_res)
