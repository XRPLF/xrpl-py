"""General XRPL Model Exceptions."""
from xrpl import XRPLException


class XRPLModelException(XRPLException):
    """General XRPL Model Exception."""

    pass


class XRPLModelValidationException(XRPLModelException):
    """XRPL Model Exception if validation fails."""

    pass
