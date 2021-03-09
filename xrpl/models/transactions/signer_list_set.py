"""
Represents a SignerListSet transaction on the XRP Ledger.

The SignerListSet transaction creates, replaces, or removes a list of signers that can
be used to multi-sign a transaction. This transaction type was introduced by the
MultiSign amendment.

`See SignerListSet <https://xrpl.org/signerlistset.html>`_
`See MultiSign Amendment <https://xrpl.org/known-amendments.html#multisign>`_
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from xrpl.models.transactions.transaction import REQUIRED, Transaction, TransactionType
from xrpl.models.utils import require_kwargs_on_init

_SIGNER_ENTRY_KEY = "SignerEntry"
_ACCOUNT_KEY = "Account"
_SIGNER_WEIGHT_KEY = "SignerWeight"


@require_kwargs_on_init
@dataclass(frozen=True)
class SignerListSet(Transaction):
    """
    Represents a SignerListSet transaction on the XRP Ledger.

    The SignerListSet transaction creates, replaces, or removes a list of signers that
    can be used to multi-sign a transaction. This transaction type was introduced by the
    MultiSign amendment.

    `See SignerListSet <https://xrpl.org/signerlistset.html>`_
    `See MultiSign Amendment <https://xrpl.org/known-amendments.html#multisign>`_
    """

    signer_quorum: int = REQUIRED
    # TODO: potentially create a SignerEntry object
    signer_entries: Optional[List[Dict[str, Dict[str, Any]]]] = None
    transaction_type: TransactionType = TransactionType.SIGNER_LIST_SET

    def _get_errors(self: SignerListSet) -> Dict[str, str]:
        errors = super()._get_errors()

        # deleting a signer list requires self.signer_quorum == 0 and
        # self.signer_entries is None
        if self.signer_quorum == 0 and self.signer_entries is not None:
            errors["signer_list_set"] = (
                "Must not include a `signer_entries` value if the signer list is being "
                "deleted."
            )
        if self.signer_quorum != 0 and self.signer_entries is None:
            errors["signer_list_set"] = (
                "Must have a value of zero for `signer_quorum` if the signer list is "
                "being deleted."
            )

        if self.signer_entries is None:  # deletion of the SignerList object
            return errors

        if self.signer_quorum <= 0:
            errors[
                "signer_quorum"
            ] = "`signer_quorum` must be greater than or equal to 0."

        if len(self.signer_entries) < 1 or len(self.signer_entries) > 8:
            errors["signer_entries"] = (
                "`signer_entries` must have at least 1 member and no more than 8 "
                "members. If this transaction is deleting the SignerList, then "
                "this parameter must be omitted."
            )
            return errors

        accounts = set()
        signer_weight_sum = 0
        for signer_entry in self.signer_entries:
            if (
                not isinstance(signer_entry, dict)
                or len(signer_entry) != 1
                or _SIGNER_ENTRY_KEY not in signer_entry
            ):
                errors["signer_entries"] = "One of the signer entries is malformed."
                return errors
            entry = signer_entry[_SIGNER_ENTRY_KEY]
            if (
                not isinstance(entry, dict)
                or len(entry) != 2
                or _ACCOUNT_KEY not in entry
                or _SIGNER_WEIGHT_KEY not in entry
            ):
                errors["signer_entries"] = "One of the signer entries is malformed."
                return errors
            entry_account = entry[_ACCOUNT_KEY]
            if self.account == entry_account:
                errors["signer_entries"] = (
                    "The account submitting the transaction cannot appear in a "
                    "signer entry."
                )
                return errors
            if entry_account in accounts:
                errors["signer_entries"] = (
                    "An account cannot appear multiple times in the list of signer "
                    "entries."
                )
                return errors
            accounts.add(entry_account)
            signer_weight_sum += entry[_SIGNER_WEIGHT_KEY]

        if self.signer_quorum > signer_weight_sum:
            errors["signer_quorum"] = (
                "`signer_quorum` must be less than or equal to the sum of the "
                "SignerWeight values in the `signer_entries` list."
            )

        return errors
