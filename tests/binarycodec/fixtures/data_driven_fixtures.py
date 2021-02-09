import json
import os

_FILENAME = "./data/data-driven-tests.json"
dirname = os.path.dirname(__file__)
absolute_path = os.path.join(dirname, _FILENAME)
with open(absolute_path) as data_driven_tests:
    _FIXTURES_JSON = json.load(data_driven_tests)
    # top level keys: ['types', 'fields_tests', 'whole_objects', 'values_tests']


def get_field_tests():
    """
    Constructs and returns a list of FieldTest objects after parsing JSON data
    describing field test fixtures.
    """
    return [
        _construct_field_test(field_test_dict)
        for field_test_dict in _FIXTURES_JSON["fields_tests"]
    ]


def get_value_tests():
    """
    Constructs and returns a list of ValueTest objects after parsing JSON data
    describing value test fixtures.
    """
    return [
        _construct_value_test(value_test_dict)
        for value_test_dict in _FIXTURES_JSON["values_tests"]
    ]


def get_whole_object_tests():
    """
    Constructs and returns a list of WholeObjectTest objects after parsing JSON data
    describing whole object test fixtures.
    """
    return [
        _construct_whole_object_test(whole_object_test_dict)
        for whole_object_test_dict in _FIXTURES_JSON["whole_objects"]
    ]


def _construct_field_test(field_test_dict):
    return FieldTest(
        field_test_dict["type_name"],
        field_test_dict["name"],
        field_test_dict["nth_of_type"],
        field_test_dict["type"],
        field_test_dict["expected_hex"],
    )


def _construct_value_test(value_test_dict):
    try:
        type_id = value_test_dict["type_id"]
    except KeyError:
        type_id = None

    try:
        is_native = value_test_dict["is_native"]
    except KeyError:
        is_native = False

    try:
        expected_hex = value_test_dict["expected_hex"]
    except KeyError:
        expected_hex = None

    try:
        is_negative = value_test_dict["is_negative"]
    except KeyError:
        is_negative = False

    try:
        type_specialisation_field = value_test_dict["type_specialisation_field"]
    except KeyError:
        type_specialisation_field = None

    try:
        error = value_test_dict["error"]
    except KeyError:
        error = None

    return ValueTest(
        value_test_dict["test_json"],
        type_id,
        value_test_dict["type"],
        is_native,
        expected_hex,
        is_negative,
        type_specialisation_field,
        error,
    )


def _construct_whole_object_test(whole_object_test_dict):
    return WholeObjectTest(
        whole_object_test_dict["tx_json"],
        whole_object_test_dict["blob_with_no_signing"],
    )


class FieldTest:
    def __init__(self, type_name, name, nth_of_type, type, expected_hex):
        self.type_name = type_name
        self.name = name
        self.nth_of_type = nth_of_type
        self.type = type
        self.expected_hex = expected_hex


class ValueTest:
    def __init__(
        self,
        test_json,
        type_id,
        type_string,
        is_native,
        expected_hex,
        is_negative,
        type_specialization_field,
        error,
    ):
        self.test_json = test_json
        self.type_id = type_id
        self.type = type_string
        self.is_native = is_native
        self.expected_hex = expected_hex
        self.is_negative = is_negative
        self.type_specialization_field = type_specialization_field
        self.error = error


class WholeObjectTest:
    def __init__(self, tx_json, expected_hex):
        self.tx_json = tx_json
        self.expected_hex = expected_hex
