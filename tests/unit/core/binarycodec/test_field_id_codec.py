from unittest import TestCase

import xrpl.core.binarycodec.field_id_codec as field_id_codec
from tests.unit.core.binarycodec.fixtures import data_driven_fixtures
from xrpl.core.binarycodec.field_id_codec import decode_ledger_header


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


class TestDecodeLedgerHeader(TestCase):
    def test_decode_ledger_header_valid(self):
        for test in data_driven_fixtures.get_ledger_data_codec_test():
            self.assertEqual(
                test["json"], decode_ledger_header(test["serialized_data"])
            )
