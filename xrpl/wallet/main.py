"""The information needed to control an XRPL account."""
from __future__ import annotations

from typing import Optional, Type

from xrpl.core.keypairs import derive_classic_address, derive_keypair, generate_seed


class Wallet:
    """The information needed to control an XRPL account."""

    def __init__(self: Wallet, public_key: str, private_key: str) -> None:
        """
        Generate a new Wallet.

        Args:
            public_key: The public key for this Wallet.
            private_key: The private key for this Wallet.
        """
        self.public_key = public_key
        self.private_key = private_key
        self.classic_address = derive_classic_address(self.public_key)
        self.next_sequence_num = 0

    @classmethod
    def create(cls: Type[Wallet], seed: Optional[str] = None) -> Wallet:
        """
        Generates a new seed and Wallet.

        Args:
            seed: A seed from which to derive public and private keys. If none
                is provided, one will be generated for you automatically (using
                Ed25519).

        Returns:
            The wallet that is generated from the given seed.
        """
        public_key, private_key = derive_keypair(seed or generate_seed())
        return cls(public_key, private_key)

    def __str__(self: Wallet) -> str:
        """
        Returns a string representation of a Wallet.

        Returns:
            A string representation of a Wallet.
        """
        return "\n".join(
            [
                f"public_key: {self.public_key}",
                "private_key: -HIDDEN-",
                f"classic_address: {self.classic_address}",
            ]
        )
