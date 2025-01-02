"""Script to generate the definitions.json file from rippled source code."""

import re
import sys

CAPITALIZATION_EXCEPTIONS = {
    "NFTOKEN": "NFToken",
    "URITOKEN": "URIToken",
    "URI": "URI",
    "UNL": "UNL",
    "XCHAIN": "XChain",
    "DID": "DID",
    "ID": "ID",
    "AMM": "AMM",
}

if len(sys.argv) != 2:
    print("Usage: python " + sys.argv[0] + " path/to/rippled")
    sys.exit(1)

########################################################################
#  Get all necessary files from rippled
########################################################################


def _read_file(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()


sfield_h_fn = sys.argv[1] + "/include/xrpl/protocol/SField.h"
sfield_macro_fn = sys.argv[1] + "/include/xrpl/protocol/detail/sfields.macro"
ledger_entries_macro_fn = (
    sys.argv[1] + "/include/xrpl/protocol/detail/ledger_entries.macro"
)
ter_h_fn = sys.argv[1] + "/include/xrpl/protocol/TER.h"
transactions_macro_fn = sys.argv[1] + "/include/xrpl/protocol/detail/transactions.macro"

sfield_h = _read_file(sfield_h_fn)
sfield_macro_file = _read_file(sfield_macro_fn)
ledger_entries_file = _read_file(ledger_entries_macro_fn)
ter_h = _read_file(ter_h_fn)
transactions_file = _read_file(transactions_macro_fn)


# Translate from rippled string format to what the binary codecs expect
def _translate(inp: str) -> str:
    if re.match(r"^UINT", inp):
        if re.search(r"256|160|128|192", inp):
            return inp.replace("UINT", "Hash")
        else:
            return inp.replace("UINT", "UInt")
    if inp == "OBJECT" or inp == "ARRAY":
        return "ST" + inp[0:1].upper() + inp[1:].lower()
    if inp == "ACCOUNT":
        return "AccountID"
    if inp == "LEDGERENTRY":
        return "LedgerEntry"
    if inp == "NOTPRESENT":
        return "NotPresent"
    if inp == "PATHSET":
        return "PathSet"
    if inp == "VL":
        return "Blob"
    if inp == "DIR_NODE":
        return "DirectoryNode"
    if inp == "PAYCHAN":
        return "PayChannel"

    parts = inp.split("_")
    result = ""
    for part in parts:
        if part in CAPITALIZATION_EXCEPTIONS:
            result += CAPITALIZATION_EXCEPTIONS[part]
        else:
            result += part[0:1].upper() + part[1:].lower()
    return result


########################################################################
#  Serialized type processing
########################################################################
print("{")
print('  "TYPES": {')
print('    "Done": -1,')

type_hits = re.findall(
    r"^ *STYPE\(STI_([^ ]*?) *, *([0-9-]+) *\) *\\?$", sfield_h, re.MULTILINE
)
if len(type_hits) == 0:
    type_hits = re.findall(
        r"^ *STI_([^ ]*?) *= *([0-9-]+) *,?$", sfield_h, re.MULTILINE
    )
for x in range(len(type_hits)):
    print(
        '    "'
        + _translate(type_hits[x][0])
        + '": '
        + type_hits[x][1]
        + ("," if x < len(type_hits) - 1 else "")
    )

print("  },")

########################################################################
#  Ledger entry type processing
########################################################################
print('  "LEDGER_ENTRY_TYPES": {')
print('    "Any": -3,')
print('    "Child": -2,')
print('    "Invalid": -1,')


def _unhex(x: str) -> str:
    if (x + "")[0:2] == "0x":
        return str(int(x, 16))
    return x


lt_hits = re.findall(
    r"^ *LEDGER_ENTRY[A-Z_]*\(lt[A-Z_]+ *, *([x0-9a-f]+) *, *([^,]+), *([^,]+), \({$",
    ledger_entries_file,
    re.MULTILINE,
)
for x in range(len(lt_hits)):
    print(
        '    "'
        + lt_hits[x][1]
        + '": '
        + _unhex(lt_hits[x][0])
        + ("," if x < len(lt_hits) - 1 else "")
    )
print("  },")

########################################################################
#  SField processing
########################################################################
print('  "FIELDS": [')
# The ones that are harder to parse directly from SField.cpp
print(
    """    [
      "Generic",
      {
        "nth": 0,
        "isVLEncoded": false,
        "isSerialized": false,
        "isSigningField": false,
        "type": "Unknown"
      }
    ],
    [
      "Invalid",
      {
        "nth": -1,
        "isVLEncoded": false,
        "isSerialized": false,
        "isSigningField": false,
        "type": "Unknown"
      }
    ],
    [
      "ObjectEndMarker",
      {
        "nth": 1,
        "isVLEncoded": false,
        "isSerialized": true,
        "isSigningField": true,
        "type": "STObject"
      }
    ],
    [
      "ArrayEndMarker",
      {
        "nth": 1,
        "isVLEncoded": false,
        "isSerialized": true,
        "isSigningField": true,
        "type": "STArray"
      }
    ],
    [
      "hash",
      {
        "nth": 257,
        "isVLEncoded": false,
        "isSerialized": false,
        "isSigningField": false,
        "type": "Hash256"
      }
    ],
    [
      "index",
      {
        "nth": 258,
        "isVLEncoded": false,
        "isSerialized": false,
        "isSigningField": false,
        "type": "Hash256"
      }
    ],
    [
      "taker_gets_funded",
      {
        "nth": 258,
        "isVLEncoded": false,
        "isSerialized": false,
        "isSigningField": false,
        "type": "Amount"
      }
    ],
    [
      "taker_pays_funded",
      {
        "nth": 259,
        "isVLEncoded": false,
        "isSerialized": false,
        "isSigningField": false,
        "type": "Amount"
      }
    ],"""
)


def _is_vl_encoded(t: str) -> str:
    if t == "VL" or t == "ACCOUNT" or t == "VECTOR256":
        return "true"
    return "false"


def _is_serialized(t: str) -> str:
    if t == "LEDGERENTRY" or t == "TRANSACTION" or t == "VALIDATION" or t == "METADATA":
        return "false"
    return "true"


def _is_signing_field(t: str, not_signing_field: str) -> str:
    if not_signing_field == "notSigning":
        return "false"
    if t == "LEDGERENTRY" or t == "TRANSACTION" or t == "VALIDATION" or t == "METADATA":
        return "false"
    return "true"


# Parse SField.cpp for all the SFields and their serialization info
sfield_hits = re.findall(
    r"^ *[A-Z]*TYPED_SFIELD *\( *sf([^,\n]*),[ \n]*([^, \n]+)[ \n]*,[ \n]*"
    r"([0-9]+)(,.*?(notSigning))?",
    sfield_macro_file,
    re.MULTILINE,
)
for x in range(len(sfield_hits)):
    print("    [")
    print('      "' + sfield_hits[x][0] + '",')
    print("      {")
    print('        "nth": ' + sfield_hits[x][2] + ",")
    print('        "isVLEncoded": ' + _is_vl_encoded(sfield_hits[x][1]) + ",")
    print('        "isSerialized": ' + _is_serialized(sfield_hits[x][1]) + ",")
    print(
        '        "isSigningField": '
        + _is_signing_field(sfield_hits[x][1], sfield_hits[x][4])
        + ","
    )
    print('        "type": "' + _translate(sfield_hits[x][1]) + '"')
    print("      }")
    print("    ]" + ("," if x < len(sfield_hits) - 1 else ""))

print("  ],")

########################################################################
#  TER code processing
########################################################################
print('  "TRANSACTION_RESULTS": {')
ter_h = str(ter_h).replace("[[maybe_unused]]", "")

ter_code_hits = re.findall(
    r"^ *((tel|tem|tef|ter|tes|tec)[A-Z_]+)( *= *([0-9-]+))? *,? *(\/\/[^\n]*)?$",
    ter_h,
    re.MULTILINE,
)
upto = -1
last = ""

for x in range(len(ter_code_hits)):
    if ter_code_hits[x][3] != "":
        upto = int(ter_code_hits[x][3])

    current = ter_code_hits[x][1]
    if current != last and last != "":
        print("")
        pass
    last = current

    print(
        '    "'
        + ter_code_hits[x][0]
        + '": '
        + str(upto)
        + ("," if x < len(ter_code_hits) - 1 else "")
    )

    upto += 1

print("  },")

########################################################################
#  Transaction type processing
########################################################################
print('  "TRANSACTION_TYPES": {')
print('    "Invalid": -1,')

tx_hits = re.findall(
    r"^ *TRANSACTION\(tt[A-Z_]+ *,* ([0-9]+) *, *([A-Za-z]+).*$",
    transactions_file,
    re.MULTILINE,
)
for x in range(len(tx_hits)):
    print(
        '    "'
        + tx_hits[x][1]
        + '": '
        + tx_hits[x][0]
        + ("," if x < len(tx_hits) - 1 else "")
    )

print("  }")
print("}")
