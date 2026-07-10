"""Optional bridge to the native Confidential MPT (XLS-0096) add-on.

Confidential MPT proof generation ships as a separate distribution,
``xrpl-py-confidential`` (import name ``xrpl.ext.confidential``), because it bundles
a native extension. The pure transaction models (``ConfidentialMPT*``) live in
xrpl-py and need no native code; only proof generation requires the add-on.
"""

from types import ModuleType


def require_confidential() -> ModuleType:
    """Return the ``xrpl.ext.confidential`` add-on module, or raise a helpful error.

    Returns:
        The imported ``xrpl.ext.confidential`` module.

    Raises:
        ImportError: If the native add-on distribution is not installed.
    """
    try:
        import xrpl.ext.confidential
    except ImportError as error:
        raise ImportError(
            "Confidential MPT proof generation requires the native add-on. "
            "Install it with:  pip install xrpl-py-confidential"
        ) from error

    return xrpl.ext.confidential
