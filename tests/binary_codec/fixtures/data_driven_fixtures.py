class DataDrivenFixtures:
    def __init__(self, field_tests):
        self.field_tests = field_tests
        # TODO: expand available sets of tests (whole_object_tests and value_tests) as needed.


class FieldTest:
    def __init__(self, type_name, name, nth_of_type, type, expected_hex):
        self.type_name = type_name
        self.name = name
        self.nth_of_type = nth_of_type
        self.type = type
        self.expected_hex = expected_hex
