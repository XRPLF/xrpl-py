"""Possible errors provided by the rippled API."""

from enum import Enum


class RippledErrorType(Enum):
    """Possible rippled error types.

    See https://xrpl.org/error-formatting.html
    """

    # TODO: decide whether to make a separate enum for non-universal errors?
    # UNIVERSAL RIPPLED ERRORS: https://xrpl.org/error-formatting.html#universal-errors

    # The server is amendment blocked and needs to be updated to the latest
    # version to stay synced with the XRP Ledger network.
    AMENDMENT_BLOCKED = "amendmentBlocked"

    # The server does not support the API version number from the request.
    INVALID_API_VERSION = "invalid_API_version"

    # (WebSocket only) The request is not a proper JSON object.
    # JSON-RPC returns a 400 Bad Request HTTP error in this case instead.
    JSON_INVALID = "jsonInvalid"

    # (WebSocket only) The request did not specify a command field.
    # JSON-RPC returns a 400 Bad Request HTTP error in this case instead.
    MISSING_COMMAND = "missingCommand"

    # The server does not have a closed ledger, typically because it has not
    # finished starting up.
    NO_CLOSED = "noClosed"

    # The server does not know what the current ledger is, due to high load, network
    # problems, validator failures, incorrect configuration, or some other problem.
    NO_CURRENT = "noCurrent"

    # The server is having trouble connecting to the rest of the XRP Ledger
    # peer-to-peer network (and is not running in stand-alone mode).
    NO_NETWORK = "noNetwork"

    # The server is under too much load to do this command right now.
    # Generally not returned if you are connected as an admin.
    TOO_BUSY = "tooBusy"

    # The request does not contain a command that the rippled server recognizes.
    UNKNOWN_CMD = "unknownCmd"

    # (WebSocket only) The request's opcode  is not text.
    WS_TEXT_REQUIRED = "wsTextRequired"

    # NON-UNIVERSAL ERROR TYPES
    ACT_BITCOIN = "actBitcoin"
    ACT_MALFORMED = "actMalformed"
    ACT_NOT_FOUND = "actNotFound"
    BAD_KEY_TYPE = "badKeyType"
    BAD_MARKET = "badMarket"
    BAD_SEED = "badSeed"
    BAD_SECRET = "badSecret"
    CHANNEL_AMT_MALFORMED = "channelAmtMalformed"
    CHANNEL_MALFORMED = "channelMalformed"
    DEPRECATED_FEATURE = "deprecatedFeature"
    DST_ACT_MALFORMED = "dstActMalformed"
    DST_ACT_NOT_FOUND = "dstActNotFound"
    DST_AMT_MALFORMED = "dstAmtMalformed"
    DST_ISR_MALFORMED = "dstIsrMalformed"
    DST_ACT_MISSING = "dstActMissing"
    ENTRY_NOT_FOUND = "entryNotFound"
    EXCESSIVE_LGR_RANGE = "excessiveLgrRange"
    FIELD_NOT_FOUND_TRANSACTION = "fieldNotFoundTransaction"
    HIGH_FEE = "highFee"
    INTERNAL = "internal"
    INTERNAL_JSON = "internalJson"
    INTERNAL_SUBMIT = "internalSubmit"
    INTERNAL_TRANSACTION = "internalTransaction"
    INVALID_HOT_WALLET = "invalidHotWallet"
    INVALID_LGR_RANGE = "invalidLgrRange"
    INVALID_PARAMS = "invalidParams"
    INVALID_TRANSACTION = "invalidTransaction"
    LGR_IDX_MALFORMED = "lgrIdxMalformed"
    LGR_IDXS_INVALID = "lgrIdxsInvalid"
    LGR_NOT_FOUND = "lgrNotFound"
    MALFORMED_ADDRESS = "malformedAddress"
    MALFORMED_CURRENCY = "malformedCurrency"
    MALFORMED_OWNER = "malformedOwner"
    MALFORMED_REQUEST = "malformedRequest"
    NO_EVENTS = "noEvents"
    NO_PATH = "noPath"
    NO_PATH_REQUEST = "noPathRequest"
    NO_PERMISSION = "noPermission"
    NOT_SUPPORTED = "notSupported"
    NOT_YET_IMPLEMENTED = "notYetImplemented"
    PUBLIC_MALFORMED = "publicMalformed"
    REPORTING_UNSUPPORTED = "reportingUnsupported"
    SRC_ACT_MALFORMED = "srcActMalformed"
    SRC_ACT_MISSING = "srcActMissing"
    SRC_ACT_NOT_FOUND = "srcActNotFound"
    SRC_CUR_MALFORMED = "srcCurMalformed"
    SRC_ISR_MALFORMED = "srcIsrMalformed"
    TRANSACTION_NOT_FOUND = "transactionNotFound"
    UNKNOWN_OPTION = "unknownOption"


class RippledException(Exception):
    """Possible errors provided by the rippled API."""

    pass
