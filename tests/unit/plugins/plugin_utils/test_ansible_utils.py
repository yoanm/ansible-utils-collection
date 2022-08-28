# -*- coding: utf-8 -*-
# (c) 2020-2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import MagicMock, patch

sys.modules['ansible'] = MagicMock()

class SimpleActionModule(unittest.TestCase):

    @patch('ansible.__version__')
    def test_basic_version(self, ansible):
        ansible.__version__ = '1.2.3'
        from ansible_collections.yoanm.utils.plugins.plugins_utils import ansible_utils

        self.assertEqual(ansible_utils.VERSION_PART, ('1', '2', '3'))

    def test_rc_version(self, ansible):
        ansible.__version__ = '1.2rc1'
        from ansible_collections.yoanm.utils.plugins.plugins_utils import ansible_utils

        self.assertEqual(ansible_utils.VERSION_PART, ('1', '2', 'rc1'))
