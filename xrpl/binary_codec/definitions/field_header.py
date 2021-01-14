class FieldHeader:
    """
    A container class for simultaneous storage of a field's type code and field code.
    """

    def __init__(self, type_code, field_code):
        self.type_code = type_code
        self.field_code = field_code

    def __eq__(self, other):
        return self.type_code == other.type_code and self.field_code == other.field_code

    def __hash__(self):
        return hash((self.type_code, self.field_code))
