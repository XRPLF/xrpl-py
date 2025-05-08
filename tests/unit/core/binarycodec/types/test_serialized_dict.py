import json
import os
from unittest import TestCase

from xrpl.core.binarycodec.binary_wrappers.binary_parser import BinaryParser
from xrpl.core.binarycodec.types.st_object import STObject

_FILENAME = "../fixtures/data/serialized-dict-fixtures.json"
dirname = os.path.dirname(__file__)
absolute_path = os.path.join(dirname, _FILENAME)
with open(absolute_path) as data_driven_tests:
    _FIXTURES_JSON = json.load(data_driven_tests)


class TestSTObject(TestCase):
    maxDiff = 1000

    def test_from_value(self):
        for test in _FIXTURES_JSON:
            expected_json = test["json"]
            buffer = test["buffer"]
            transaction = STObject.from_value(expected_json)
            self.assertEqual(buffer, str(transaction).upper())

    def test_from_value_to_json(self):
        for test in _FIXTURES_JSON:
            expected_json = test["json"]
            transaction = STObject.from_value(expected_json)
            self.assertEqual(transaction.to_json(), expected_json)

    def test_from_parser_to_json(self):
        for test in _FIXTURES_JSON:
            expected_json = test["json"]
            buffer = test["buffer"]
            parser = BinaryParser(buffer)
            transaction = STObject.from_parser(parser)
            self.assertEqual(transaction.to_json(), expected_json)
