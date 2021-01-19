"""A container class for simultaneous storage of a field's type code and field code."""
# Allows the use of a type inside the class that defines it.
from __future__ import annotations


class FieldHeader:
    """A container class for simultaneous storage of a field's type code and
    field code.
    """

    def __init__(self, type_code: int, field_code: int):
        """
        Construct a FieldHeader.
        `See Field Order <https://xrpl.org/serialization.html#canonical-field-order>`_

        :param type_code: The code for this field's serialization type.
        :param field_code: The sort code that orders fields of the same type.
        """
        self.type_code = type_code
        self.field_code = field_code

    def __eq__(self, other: FieldHeader):
        """Two FieldHeaders are equal if both type code and field_code are the same."""
        return self.type_code == other.type_code and self.field_code == other.field_code

    def __hash__(self):
        """Two equal FieldHeaders must have the same hash value."""
        return hash((self.type_code, self.field_code))
