from unittest import TestCase

import xrpl.core.binarycodec.field_id_codec as field_id_codec
from tests.unit.core.binarycodec.fixtures import data_driven_fixtures


class TestFieldIDCodec(TestCase):
    """`See FieldIDs <https://xrpl.org/serialization.html#field-ids>`_."""

    def setUp(self):
        self.field_tests = data_driven_fixtures.get_field_tests()

    def test_encode(self):
        for test in self.field_tests:
            # .hex().upper() just formats the resulting bytes for comparison
            # with upper case hex string in fixture data
            self.assertEqual(
                test.expected_hex, field_id_codec.encode(test.name).hex().upper()
            )

    def test_decode(self):
        for test in self.field_tests:
            self.assertEqual(test.name, field_id_codec.decode(test.expected_hex))
