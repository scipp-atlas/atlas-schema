"""
Typing helpers.
"""

from __future__ import annotations

import sys
from typing import Dict, Type

import awkward

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

Behavior: TypeAlias = Dict[str, Type[awkward.Record]]

__all__ = ("Annotated", "Behavior", "Self")
