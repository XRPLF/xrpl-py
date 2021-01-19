"""TODO: D100 Missing docstring in public module."""


class FieldHeader:
    """A container class for simultaneous storage of a field's type code and
    field code.
    """

    def __init__(self, type_code, field_code):
        """TODO: D107 Missing docstring in __init__."""
        self.type_code = type_code
        self.field_code = field_code

    def __eq__(self, other):
        """TODO: D105 Missing docstring in magic method."""
        return self.type_code == other.type_code and self.field_code == other.field_code

    def __hash__(self):
        """TODO: D105 Missing docstring in magic method."""
        return hash((self.type_code, self.field_code))
