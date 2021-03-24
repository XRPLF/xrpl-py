"""The information needed to control an XRPL account."""
from __future__ import annotations

from typing import Optional, cast

from xrpl import CryptoAlgorithm, XRPLException
from xrpl.core.keypairs import derive_classic_address, derive_keypair, generate_seed


class Wallet:
    """The information needed to control an XRPL account."""

    def __init__(
        self: Wallet,
        seed: Optional[str] = None,
        pub_key: Optional[str] = None,
        priv_key: Optional[str] = None,
    ) -> None:
        """
        Generate a new Wallet. There are three ways to instantiate a Wallet:

        1) Explicitly with each key: in this case, you must pass both pub_key
        and priv_key. The seed argument will not have an effect.

        2) Generated from a seed: in this case, you must pass only the seed
        argument.

        3) Generated from entropy: in this case, you must pass no arguments
        and the seed with be generated for you.

        Args:
            seed: The seed from which public and private keys are derived.
            pub_key: The public key of this Wallet.
            priv_key: The private key of this Wallet.

        Raises:
            XRPLException: If pub_key is passed without priv_key, or priv_key
            is passed without pub_key.
        """
        if (pub_key is None) ^ (priv_key is None):
            raise XRPLException(
                "Must pass both pub_key and priv_key or neither",
            )
        if pub_key is not None:
            self.seed = None
            self.pub_key = pub_key
            # have to cast because mypy doesn't realize priv_key must be
            # not-None here
            self.priv_key = cast(str, priv_key)
        else:
            self.seed = seed or generate_seed(algorithm=CryptoAlgorithm.SECP256K1)
            self.pub_key, self.priv_key = derive_keypair(self.seed)
        self.classic_address = derive_classic_address(self.pub_key)
        self.next_sequence_num = 0

    def __str__(self: Wallet) -> str:
        """
        Returns a string representation of a Wallet.

        Returns:
            A string representation of a Wallet.
        """
        return (
            f"seed: {self.seed}\npub_key: {self.pub_key}\n"
            f"priv_key: -HIDDEN-\nclassic_address: {self.classic_address}\n"
        )
