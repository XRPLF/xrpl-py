import json
import os

# TODO: expand the set of test classes here to include "WholeObject"
# TODO: functions to parse "whole_objects" dicts into WholeObjectTest lists


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
    for test in _FIXTURES_JSON["values_tests"][10:13]:
        print(test)

    return [
        _construct_value_test(value_test_dict)
        for value_test_dict in _FIXTURES_JSON["values_tests"]
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

    def __str__(self):
        return (
            "test_json: "
            + str(self.test_json)
            + " "
            + str(type(self.test_json))
            + "\ntype_id: "
            + str(self.type_id)
            + " "
            + str(type(self.type_id))
            + "\ntype: "
            + str(self.type)
            + " "
            + str(type(self.type))
            + "\nis_native: "
            + str(self.is_native)
            + " "
            + str(type(self.is_native))
            + "\nexpected_hex: "
            + str(self.expected_hex)
            + " "
            + str(type(self.expected_hex))
            + "\nis_negative: "
            + str(self.is_negative)
            + " "
            + str(type(self.is_negative))
            + "\ntype_specialization_field: "
            + str(self.type_specialization_field)
            + " "
            + str(type(self.type_specialization_field))
            + "\nerror: "
            + str(self.error)
            + "\n"
        )
