import json


class DefinitionService:
    ''' Service for accessing XRPL type and field metadata from definitions.json.'''

    def __init__(self):
        self.definitions = self.load_definitions()


    def load_definitions(fname='definitions.json'):
        """
        Loads JSON from the definitions file and converts it to a preferred format.

        (The definitions file should be drop-in compatible with the one from the
        ripple-binary-codec JavaScript package.)
        """
        with open(fname) as definitions_file:
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