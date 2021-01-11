import unittest

from xrpl import binary_codec

class TestDefinitionService(unittest.TestCase):
    def setUp(self):
        self.definition_service = binary_codec.DefinitionService()

    def test_load_definitions(self):
        definitions = self.definition_service.load_definitions()
        expected_keys = ["TYPES", "FIELDS", "TRANSACTION_RESULTS", "TRANSACTION_TYPES"]
        for key in expected_keys:
            self.assertIn(key, definitions)
