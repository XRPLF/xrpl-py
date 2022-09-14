"""
A path is an ordered array. Each member of a path is an
object that specifies the step.
"""

from __future__ import annotations

from typing import List

from xrpl.models.path_step import PathStep

Path = List[PathStep]
"""
A Path is an ordered array of PathSteps.
"""
