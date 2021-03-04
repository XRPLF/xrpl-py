"""
Paths define a way for payments to flow through intermediary steps
on their way from sender to receiver. Paths enable cross-currency
payments by connecting sender and receiver through order books.
Use these methods to work with paths and other books.
"""
from xrpl.models.requests.paths.book_offers import BookOffers
from xrpl.models.requests.paths.deposit_authorized import DepositAuthorized
from xrpl.models.requests.paths.path_find import PathFind
from xrpl.models.requests.paths.ripple_path_find import RipplePathFind

__all__ = [
    "BookOffers",
    "DepositAuthorized",
    "PathFind",
    "RipplePathFind",
]
