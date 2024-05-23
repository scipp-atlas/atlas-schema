"""
Typing helpers.
"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

__all__ = ("Annotated",)
