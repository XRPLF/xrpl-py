import json
import os
from .field_header import FieldHeader
from .field_info import FieldInfo


class DefinitionService:
    """ Service for accessing XRPL type and field metadata from definitions.json."""

    def __init__(self):
        self.definitions = self.load_definitions()
        self.transaction_type_code_to_str_map = {
            value: key for (key, value) in self.definitions["TRANSACTION_TYPES"].items()
        }
        self.transaction_results_code_to_str_map = {
            value: key for (key, value) in self.definitions["TRANSACTION_RESULTS"].items()
        }

        self.type_ordinal_map = self.definitions["TYPES"]
        self.field_info_map = {}
        self.field_header_name_map = {}

        for field_name in self.definitions["FIELDS"]:
            field_entry = self.definitions["FIELDS"][field_name]
            field_info = FieldInfo(field_entry["nth"],
                                   field_entry["isVLEncoded"],
                                   field_entry["isSerialized"],
                                   field_entry["isSigningField"],
                                   field_entry["type"])
            field_header = FieldHeader(self.type_ordinal_map[field_entry["type"]], field_entry["nth"])
            self.field_info_map[field_name] = field_info
            self.field_header_name_map[field_header] = field_name
            # TODO: error handling

    def load_definitions(self, filename='definitions.json'):
        """
        Loads JSON from the definitions file and converts it to a preferred format.

        :param filename: The name of the definitions file.  (The definitions file should be drop-in compatible with the
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
                "FIELDS": {k: v for (k, v) in definitions["FIELDS"]},  # convert list of tuples to dict
                # field_name str: {
                #   nth: field_sort_key int,
                #   isVLEncoded: bool,
                #   isSerialized: bool,
                #   isSigningField: bool,
                #   type: type_name str
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
        return self.field_info_map[field_name].type

    def get_field_type_code(self, field_name):
        """
        Returns the type code associated with the given field.
        `Serialization Type Codes <https://xrpl.org/serialization.html#type-codes>`_
        """
        field_type_name = self.get_field_type_name(field_name)
        return self.type_ordinal_map[field_type_name]

    def get_field_code(self, field_name):
        """
        Returns the field code associated with the given field.
        `Serializtion Field Codes <https://xrpl.org/serialization.html#field-codes>`_
        """
        return self.field_info_map[field_name].nth

    def get_field_sort_key(self, field_name):
        """
        Returns a tuple sort key for a given field name.
        `Serialization Canonical Field Order <https://xrpl.org/serialization.html#canonical-field-order>`_
        """
        return self.get_field_type_code(field_name), self.get_field_code(field_name)

    def get_field_header_from_name(self, field_name):
        """
        Returns a FieldHeader object for a field of the given field name.
        """
        return FieldHeader(self.get_field_type_code(field_name), self.get_field_code(field_name))

    def get_field_name_from_header(self, field_header):
        """
        Returns the field name described by the given FieldHeader object.
        """
        return self.field_header_name_map[field_header]
