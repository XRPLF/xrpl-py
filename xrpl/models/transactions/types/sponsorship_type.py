"""Enum containing the different Sponsorship types."""

from enum import Enum


class SponsorshipType(int, Enum):
    """
    Enum representing the type of sponsorship in a Sponsorship ledger entry
    or SponsorshipSet transaction.

    See XLS-0068 Sponsored Fees and Reserves specification for details.
    """

    FEE = 0x00000001
    """
    Fee sponsorship - the sponsor pays transaction fees on behalf of the sponsee.
    """

    RESERVE = 0x00000002
    """
    Reserve sponsorship - the sponsor pays reserve requirements on behalf of the sponsee.
    """

