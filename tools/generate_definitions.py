"""Script to generate the definitions.json file from rippled source code."""

import re
import sys

import httpx

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
    print(
        "Usage: python " + sys.argv[0] + " github.com/user/rippled/tree/feature-branch"
    )
    sys.exit(1)

########################################################################
#  Get all necessary files from rippled
########################################################################


def _read_file_from_github(repo: str, filename: str) -> str:
    url = repo.replace("github.com", "raw.githubusercontent.com")
    url = url.replace("tree", "refs/heads")
    url += filename
    if not url.startswith("http"):
        url = "https://" + url
    response = httpx.get(url)
    return response.text


def _read_file(folder: str, filename: str) -> str:
    with open(folder + filename, "r") as f:
        return f.read()


func = _read_file_from_github if "github.com" in sys.argv[1] else _read_file

sfield_h = func(sys.argv[1], "/include/xrpl/protocol/SField.h")
sfield_macro_file = func(sys.argv[1], "/include/xrpl/protocol/detail/sfields.macro")
ledger_entries_file = func(
    sys.argv[1], "/include/xrpl/protocol/detail/ledger_entries.macro"
)
ter_h = func(sys.argv[1], "/include/xrpl/protocol/TER.h")
transactions_file = func(
    sys.argv[1], "/include/xrpl/protocol/detail/transactions.macro"
)


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


# start
print("{")

########################################################################
#  SField processing
########################################################################
print('  "FIELDS": [')

# The ones that are harder to parse directly from SField.cpp
print(
    """    [
      "Generic",
      {
        "isSerialized": false,
        "isSigningField": false,
        "isVLEncoded": false,
        "nth": 0,
        "type": "Unknown"
      }
    ],
    [
      "Invalid",
      {
        "isSerialized": false,
        "isSigningField": false,
        "isVLEncoded": false,
        "nth": -1,
        "type": "Unknown"
      }
    ],
    [
      "ObjectEndMarker",
      {
        "isSerialized": true,
        "isSigningField": true,
        "isVLEncoded": false,
        "nth": 1,
        "type": "STObject"
      }
    ],
    [
      "ArrayEndMarker",
      {
        "isSerialized": true,
        "isSigningField": true,
        "isVLEncoded": false,
        "nth": 1,
        "type": "STArray"
      }
    ],
    [
      "taker_gets_funded",
      {
        "isSerialized": false,
        "isSigningField": false,
        "isVLEncoded": false,
        "nth": 258,
        "type": "Amount"
      }
    ],
    [
      "taker_pays_funded",
      {
        "isSerialized": false,
        "isSigningField": false,
        "isVLEncoded": false,
        "nth": 259,
        "type": "Amount"
      }
    ],"""
)

type_hits = re.findall(
    r"^ *STYPE\(STI_([^ ]*?) *, *([0-9-]+) *\) *\\?$", sfield_h, re.MULTILINE
)
if len(type_hits) == 0:
    type_hits = re.findall(
        r"^ *STI_([^ ]*?) *= *([0-9-]+) *,?$", sfield_h, re.MULTILINE
    )
type_map = {x[0]: x[1] for x in type_hits}


def _is_vl_encoded(t: str) -> str:
    if t == "VL" or t == "ACCOUNT" or t == "VECTOR256":
        return "true"
    return "false"


def _is_serialized(t: str, name: str) -> str:
    if t == "LEDGERENTRY" or t == "TRANSACTION" or t == "VALIDATION" or t == "METADATA":
        return "false"
    if name == "hash" or name == "index":
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
sfield_hits += [
    ("hash", "UINT256", "257", "", "notSigning"),
    ("index", "UINT256", "258", "", "notSigning"),
]
sfield_hits.sort(key=lambda x: int(type_map[x[1]]) * 2**16 + int(x[2]))
for x in range(len(sfield_hits)):
    print("    [")
    print('      "' + sfield_hits[x][0] + '",')
    print("      {")
    print(
        '        "isSerialized": '
        + _is_serialized(sfield_hits[x][1], sfield_hits[x][0])
        + ","
    )
    print(
        '        "isSigningField": '
        + _is_signing_field(sfield_hits[x][1], sfield_hits[x][4])
        + ","
    )
    print('        "isVLEncoded": ' + _is_vl_encoded(sfield_hits[x][1]) + ",")
    print('        "nth": ' + sfield_hits[x][2] + ",")
    print('        "type": "' + _translate(sfield_hits[x][1]) + '"')
    print("      }")
    print("    ]" + ("," if x < len(sfield_hits) - 1 else ""))

print("  ],")

########################################################################
#  Ledger entry type processing
########################################################################
print('  "LEDGER_ENTRY_TYPES": {')


def _unhex(x: str) -> str:
    if (x + "")[0:2] == "0x":
        return str(int(x, 16))
    return x


lt_hits = re.findall(
    r"^ *LEDGER_ENTRY[A-Z_]*\(lt[A-Z_]+ *, *([x0-9a-f]+) *, *([^,]+), *([^,]+), \({$",
    ledger_entries_file,
    re.MULTILINE,
)
lt_hits.append(("-1", "Invalid"))
lt_hits.sort(key=lambda x: x[1])
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
#  TER code processing
########################################################################
print('  "TRANSACTION_RESULTS": {')
ter_h = str(ter_h).replace("[[maybe_unused]]", "")

ter_code_hits = re.findall(
    r"^ *((tel|tem|tef|ter|tes|tec)[A-Z_]+)( *= *([0-9-]+))? *,? *(\/\/[^\n]*)?$",
    ter_h,
    re.MULTILINE,
)
ter_codes = []
upto = -1

for x in range(len(ter_code_hits)):
    if ter_code_hits[x][3] != "":
        upto = int(ter_code_hits[x][3])
    ter_codes.append((ter_code_hits[x][0], upto))

    upto += 1

ter_codes.sort(key=lambda x: x[0])
current_type = ""
for x in range(len(ter_codes)):
    if current_type == "":
        current_type = ter_codes[x][0][:3]
    elif current_type != ter_codes[x][0][:3]:
        print("")
        current_type = ter_codes[x][0][:3]

    print(
        '    "'
        + ter_codes[x][0]
        + '": '
        + str(ter_codes[x][1])
        + ("," if x < len(ter_codes) - 1 else "")
    )

print("  },")

########################################################################
#  Transaction type processing
########################################################################
print('  "TRANSACTION_TYPES": {')

tx_hits = re.findall(
    r"^ *TRANSACTION\(tt[A-Z_]+ *,* ([0-9]+) *, *([A-Za-z]+).*$",
    transactions_file,
    re.MULTILINE,
)
tx_hits.append(("-1", "Invalid"))
tx_hits.sort(key=lambda x: x[1])
for x in range(len(tx_hits)):
    print(
        '    "'
        + tx_hits[x][1]
        + '": '
        + tx_hits[x][0]
        + ("," if x < len(tx_hits) - 1 else "")
    )

print("  },")

########################################################################
#  Serialized type processing
########################################################################
print('  "TYPES": {')

type_hits.append(("DONE", "-1"))
type_hits.sort(key=lambda x: _translate(x[0]))
for x in range(len(type_hits)):
    print(
        '    "'
        + _translate(type_hits[x][0])
        + '": '
        + type_hits[x][1]
        + ("," if x < len(type_hits) - 1 else "")
    )

print("  }")
print("}")
