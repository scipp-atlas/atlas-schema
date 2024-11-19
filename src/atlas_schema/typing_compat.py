"""
Typing helpers.
"""

from __future__ import annotations

import sys
from typing import Annotated

import awkward

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

Behavior: TypeAlias = dict[str, type[awkward.Record]]

__all__ = ("Annotated", "Behavior", "Self")
