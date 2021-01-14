import json
import os


class DefinitionService:
    """ Service for accessing XRPL type and field metadata from definitions.json."""

    def __init__(self):
        self.definitions = self.load_definitions()

    def load_definitions(self, filename="definitions.json"):
        """
        Loads JSON from the definitions file and converts it to a preferred format.

        :param filename: The name of the definitions file.
        (The definitions file should be drop-in compatible with the
        one from the ripple-binary-codec JavaScript package.)

        :return: A dictionary containing the mappings provided in the definitions file.
        """
        dirname = os.path.dirname(__file__)
        absolute_path = os.path.join(dirname, filename)
        with open(absolute_path) as definitions_file:
            definitions = json.load(definitions_file)
            return {
                "TYPES": definitions["TYPES"],
                # type_name str: type_sort_key int
                "FIELDS": {
                    k: v for (k, v) in definitions["FIELDS"]
                },  # convert list of tuples to dict
                # field_name str: {
                #   nth: field_sort_key int,
                #   isVLEncoded: bool,
                #   isSerialized: bool,
                #   isSigningField: bool,
                #   type: str
                # }
                "LEDGER_ENTRY_TYPES": definitions["LEDGER_ENTRY_TYPES"],
                "TRANSACTION_RESULTS": definitions["TRANSACTION_RESULTS"],
                "TRANSACTION_TYPES": definitions["TRANSACTION_TYPES"],
            }

    def get_field_type_name(self, field_name):
        """
        Returns the serialization data type for the given field name.
        `Serialization Type List <https://xrpl.org/serialization.html#type-list>`_
        """
        return self.definitions["FIELDS"][field_name]["type"]

    def get_field_type_code(self, field_name):
        """
        Returns the type code associated with the given field.
        `Serialization Type Codes <https://xrpl.org/serialization.html#type-codes>`_
        """
        field_type_name = self.get_field_type_name(field_name)
        return self.definitions["TYPES"][field_type_name]

    def get_field_code(self, field_name):
        """
        Returns the field code associated with the given field.
        `Serializtion Field Codes <https://xrpl.org/serialization.html#field-codes>`_
        """
        return self.definitions["FIELDS"][field_name]["nth"]

    def get_field_sort_key(self, field_name):
        """
        Returns a tuple sort key for a given field name.
        `Serialization Canonical Field Order
        <https://xrpl.org/serialization.html#canonical-field-order>`_
        """
        return self.get_field_type_code(field_name), self.get_field_code(field_name)

    # TODO: get_field_name(self, field_id)
    # For deserialization. May require inverse table for lookup.
