class FieldHeader:
    """
    A container class for simultaneous storage of a field's type code and field code.
    """
    def __init__(self, type_code, field_code):
        self.type_code = type_code
        self.field_code = field_code