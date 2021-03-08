"""TODO: docstring"""

from __future__ import annotations

from xrpl.keypairs.main import derive_classic_address, derive_keypair


class Wallet:
    """The information needed to control an XRPL account."""

    def __init__(self: Wallet, seed: str):
        """Generate a new Wallet."""
        self.pub_key, self.priv_key = derive_keypair(self.seed)
        self.classic_address = derive_classic_address(self.pub_key)
        self.next_sequence_num = None

    def __str__(self: Wallet):
        """Returns a string representation of a wallet."""
        return "seed: {}\npub_key: {}\npriv_key: {}\nclassic_address: {}\n".format(
            self.seed, self.pub_key, self.priv_key, self.classic_address
        )
