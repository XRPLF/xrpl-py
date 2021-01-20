"""A collection of serialization information about a specific field type."""
from xrpl.binary_codec.definitions.field_info import FieldInfo
from xrpl.binary_codec.definitions.field_header import FieldHeader


class FieldInstance:
    """A collection of serialization information about a specific field type."""

    def __init__(
        self,
        field_info: FieldInfo,
        field_name: str,
        field_header: FieldHeader,
    ):
        """
        Construct a FieldInstance.

        :param field_info: The field's serialization info from definitions.json.
        :param field_name: The field's string name.
        :param field_header: A FieldHeader object with the type_code and field_code.
        """
        self.nth = field_info.nth
        self.is_variable_length_encoded = field_info.is_variable_length_encoded
        self.is_serialized = field_info.is_serialized
        self.is_signing = field_info.is_signing_field
        self.type = field_info.type
        self.name = field_name
        self.header = field_header
        self.ordinal = self.header.type_code << 16 | self.nth
