"""Model for DirectoryNodeEntryDirectoryOneOf."""

from dataclasses import dataclass
from typing import Optional
from xrpl.models.base_model import BaseModel
from xrpl.models.utils import require_kwargs_on_init


@require_kwargs_on_init
@dataclass(frozen=True)
class DirectoryNodeEntryDirectoryOneOf(BaseModel):
    sub_index: Optional[int] = None
    dir_root: Optional[str] = None
    owner: Optional[str] = None
