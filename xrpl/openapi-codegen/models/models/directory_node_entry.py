"""Model for DirectoryNodeEntry."""

from dataclasses import dataclass
from typing import Optional, Union
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DirectoryNodeEntry(BaseModel):
    """
    Retrieve a DirectoryNode, which contains a list of other ledger objects.
    """

    directory: Optional[Union[str, DirectoryNodeEntryDirectoryOneOf]] = None
