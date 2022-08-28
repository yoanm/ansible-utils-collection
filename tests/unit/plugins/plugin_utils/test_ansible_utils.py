# -*- coding: utf-8 -*-
# (c) 2020-2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    # Python 3.4+
    from importlib import reload  # type: ignore
except ImportError:
    try:
        # Python 3,<3.4
        from imp import reload  # type: ignore
    except ImportError:
        pass  # < python 3, method globally defined
from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.yoanm.utils.plugins.plugin_utils import ansible_utils


class SimpleActionModule(unittest.TestCase):

    @patch('ansible.__version__', '1.2.3')
    def test_basic_version(self):
        reload(ansible_utils)  # Reload module else ansible.__version__ is the one defined during previous test
        self.assertEqual(['1', '2', '3'], ansible_utils.VERSION_PART)
        self.assertEqual('1.2', ansible_utils.SHORT_VERSION)
        self.assertEqual(1.2, ansible_utils.SHORT_VERSION_FLOAT)

    @patch('ansible.__version__', '1.2rc1')
    def test_rc_version(self):
        reload(ansible_utils)  # Reload module else ansible.__version__ is the one defined during previous test
        self.assertEqual(['1', '2', 'rc1'], ansible_utils.VERSION_PART)
        self.assertEqual('1.2', ansible_utils.SHORT_VERSION)
        self.assertEqual(1.2, ansible_utils.SHORT_VERSION_FLOAT)
