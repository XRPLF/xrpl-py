class FieldInstance:
    def __init__(
        self,
        nth,
        is_variable_length_encoded,
        is_serialized,
        is_signing,
        type_code,
        name,
        header,
    ):
        self.nth = nth
        self.is_variable_length_encoded = is_variable_length_encoded
        self.is_serialized = is_serialized
        self.is_signing = is_signing
        self.type_code = type_code
        self.name = name
        self.header = header
        self.ordinal = self.header.type_code << 16 | nth
