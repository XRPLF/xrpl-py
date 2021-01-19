"""TODO: D100 Missing docstring in pubic module."""


class FieldInstance:
    """TODO: D101 Missing docstring in public class."""

    def __init__(
        self,
        field_info,
        field_name,
        field_header,
    ):
        """TODO: D107 Missing docstring in __init__."""
        self.nth = field_info.nth
        self.is_variable_length_encoded = field_info.is_variable_length_encoded
        self.is_serialized = field_info.is_serialized
        self.is_signing = field_info.is_signing
        self.type = field_info.type
        self.name = field_name
        self.header = field_header
        self.ordinal = self.header.type_code << 16 | self.nth
