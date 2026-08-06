"""Public entry point for the native Confidential MPT (XLS-0096) add-on.

Confidential MPT proof generation ships as a separate distribution,
``xrpl-py-confidential`` (import name ``xrpl.ext.confidential``), because it bundles
a native extension. The pure transaction models (``ConfidentialMPT*``) live in
xrpl-py and need no native code; only proof generation requires the add-on.

``require_confidential`` is re-exported from :mod:`xrpl.core`, so the canonical
way to reach the add-on from core xrpl-py is::

    from xrpl.core import require_confidential

    confidential = require_confidential()  # raises a helpful error if not installed
    tx = confidential.prepare_confidential_send(client, ...)
"""

from types import ModuleType


def require_confidential() -> ModuleType:
    """Return the ``xrpl.ext.confidential`` add-on module, or raise a helpful error.

    This is the recommended entry point for loading the confidential add-on: it
    fails with an actionable ``pip install`` message when the native
    distribution is missing, instead of a bare ``ModuleNotFoundError``.

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
