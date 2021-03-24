"""The information needed to control an XRPL account."""
from __future__ import annotations

from typing import Optional, Type

from xrpl.core.keypairs import derive_classic_address, derive_keypair, generate_seed


class Wallet:
    """The information needed to control an XRPL account."""

    def __init__(self: Wallet, pub_key: str, priv_key: str) -> None:
        """
        Generate a new Wallet.

        Args:
            pub_key: The public key for this Wallet.
            priv_key: The private key for this Wallet.
        """
        self.pub_key = pub_key
        self.priv_key = priv_key
        self.classic_address = derive_classic_address(self.pub_key)
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
        pub_key, priv_key = derive_keypair(seed or generate_seed())
        return cls(pub_key, priv_key)

    def __str__(self: Wallet) -> str:
        """
        Returns a string representation of a Wallet.

        Returns:
            A string representation of a Wallet.
        """
        return "\n".join(
            [
                f"pub_key: {self.pub_key}",
                "priv_key: -HIDDEN-",
                f"classic_address: {self.classic_address}",
            ]
        )
