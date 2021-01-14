from .data_driven_fixtures import FieldTest
import json
import os


# TODO: functions to parse "whole_objects" and "values_tests" dicts into WholeObjectTest and ValueTest lists as needed

def get_field_tests(filename="./data/data-driven-tests.json"):
    """
    Constructs and returns a list of FieldTest objects after parsing JSON data describing field test fixtures.
    """
    dirname = os.path.dirname(__file__)
    absolute_path = os.path.join(dirname, filename)
    with open(absolute_path) as data_driven_tests:
        fixtures_json = json.load(data_driven_tests)
        # top level keys: ['types', 'fields_tests', 'whole_objects', 'values_tests']

    # parse "fields_tests" into list of FieldTest objects
    return [construct_field_test(field_test_dict) for field_test_dict in fixtures_json["fields_tests"]]


def construct_field_test(field_test_dict):
    return FieldTest(
        field_test_dict["type_name"],
        field_test_dict["name"],
        field_test_dict["nth_of_type"],
        field_test_dict["type"],
        field_test_dict["expected_hex"]
    )
