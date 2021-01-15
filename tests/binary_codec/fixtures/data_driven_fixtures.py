import json
import os

# TODO: expand the set of test classes here as `WholeObjectTest` and `ValueTest`
#  become relevant.
# TODO: functions to parse "whole_objects" and "values_tests" dicts into WholeObjectTest
#  and ValueTest lists as needed


def get_field_tests(filename="./data/data-driven-tests.json"):
    """
    Constructs and returns a list of FieldTest objects after parsing JSON data
    describing field test fixtures.
    """
    dirname = os.path.dirname(__file__)
    absolute_path = os.path.join(dirname, filename)
    with open(absolute_path) as data_driven_tests:
        fixtures_json = json.load(data_driven_tests)
        # top level keys: ['types', 'fields_tests', 'whole_objects', 'values_tests']
    return [
        _construct_field_test(field_test_dict)
        for field_test_dict in fixtures_json["fields_tests"]
    ]


def _construct_field_test(field_test_dict):
    return FieldTest(
        field_test_dict["type_name"],
        field_test_dict["name"],
        field_test_dict["nth_of_type"],
        field_test_dict["type"],
        field_test_dict["expected_hex"],
    )


class FieldTest:
    def __init__(self, type_name, name, nth_of_type, type, expected_hex):
        self.type_name = type_name
        self.name = name
        self.nth_of_type = nth_of_type
        self.type = type
        self.expected_hex = expected_hex
