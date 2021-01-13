import unittest

from xrpl import binary_codec


class TestDefinitionService(unittest.TestCase):
    def setUp(self):
        self.definition_service = binary_codec.DefinitionService()
        self.test_field_name = "Sequence"

    def test_load_definitions(self):
        expected_keys = ["TYPES", "FIELDS", "TRANSACTION_RESULTS", "TRANSACTION_TYPES"]
        for key in expected_keys:
            self.assertIn(key, self.definition_service.definitions)

    def test_get_field_type_name(self):
        expected_field_type_name = "UInt32"
        field_type_name = self.definition_service.get_field_type_name(self.test_field_name)
        self.assertEqual(expected_field_type_name, field_type_name)

    def test_get_field_type_code(self):
        expected_field_type_code = 2
        field_type_code = self.definition_service.get_field_type_code(self.test_field_name)
        self.assertEqual(expected_field_type_code, field_type_code)

    def test_get_field_code(self):
        expected_field_code = 4
        field_code = self.definition_service.get_field_code(self.test_field_name)
        self.assertEqual(expected_field_code, field_code)

    def test_get_field_sort_key(self):
        expected_field_sort_key = (2, 4)
        field_sort_key = self.definition_service.get_field_sort_key(self.test_field_name)
        print("field sort key:", field_sort_key)
        self.assertEqual(expected_field_sort_key, field_sort_key)
