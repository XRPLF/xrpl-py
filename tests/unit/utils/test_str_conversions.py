from unittest import TestCase

import xrpl.utils

_ORIGINAL = "https://en.wikipedia.org/wiki/Sunn_O%29%29%29"
_HEX = """\
68747470733a2f2f656e2e77696b6970656469612e6f72672f7769\
6b692f53756e6e5f4f253239253239253239\
"""


class TestStrConversions(TestCase):
    def test_str_to_hex(self):
        self.assertTrue(xrpl.utils.str_to_hex(_ORIGINAL) == _HEX)

    def test_hex_to_str(self):
        self.assertTrue(xrpl.utils.hex_to_str(_HEX) == _ORIGINAL)
