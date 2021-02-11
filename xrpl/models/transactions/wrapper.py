"""DOCSTRING"""
from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class Wrapper(ABC, str):
    """A typed wrapper for single values."""

    value: str
