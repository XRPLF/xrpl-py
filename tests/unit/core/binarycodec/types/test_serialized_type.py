from unittest import TestCase

from tests.unit.core.binarycodec.fixtures.data_driven_fixtures import (
    ValueTest,
    get_value_tests,
)
from xrpl.core.binarycodec.exceptions import XRPLBinaryCodecException
from xrpl.core.binarycodec.types.account_id import AccountID
from xrpl.core.binarycodec.types.amount import Amount
from xrpl.core.binarycodec.types.blob import Blob
from xrpl.core.binarycodec.types.currency import Currency
from xrpl.core.binarycodec.types.hash128 import Hash128
from xrpl.core.binarycodec.types.hash160 import Hash160
from xrpl.core.binarycodec.types.hash256 import Hash256
from xrpl.core.binarycodec.types.path_set import PathSet
from xrpl.core.binarycodec.types.serialized_type import SerializedType
from xrpl.core.binarycodec.types.uint8 import UInt8
from xrpl.core.binarycodec.types.uint16 import UInt16
from xrpl.core.binarycodec.types.uint32 import UInt32
from xrpl.core.binarycodec.types.uint64 import UInt64
from xrpl.core.binarycodec.types.vector256 import Vector256

TYPE_MAP = {
    "AccountID": AccountID,
    "Amount": Amount,
    "Blob": Blob,
    "Currency": Currency,
    "Hash128": Hash128,
    "Hash160": Hash160,
    "Hash256": Hash256,
    "PathSet": PathSet,
    "UInt8": UInt8,
    "UInt16": UInt16,
    "UInt32": UInt32,
    "UInt64": UInt64,
    "Vector256": Vector256,
}

VALUE_TESTS = get_value_tests()


def data_driven_fixtures_for_type(type_string: str):
    """Return a list of ValueTest objects for the specified type."""
    return [value_test for value_test in VALUE_TESTS if value_test.type == type_string]


class TestSerializedType(TestCase):
    def fixture_test(self, fixture: ValueTest):
        """Run the appropriate test for given fixture case."""
        serialized_type: SerializedType = TYPE_MAP[fixture.type]
        if type(fixture.test_json) == dict:
            json_value = fixture.test_json
        else:
            json_value = str(fixture.test_json)
        if fixture.error is not None:
            self.assertRaises(
                XRPLBinaryCodecException, serialized_type.from_value, json_value
            )
        else:
            self.assertEqual(
                serialized_type.from_value(json_value).to_hex(),
                fixture.expected_hex,
            )
