from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, TypeVar

AttrValue = TypeVar("AttrValue")


@contextmanager
def attr_as(obj, field: str, value: Any) -> Iterator[AttrValue]:
    old_value = getattr(obj, field)
    setattr(obj, field, value)
    yield old_value
    setattr(obj, field, old_value)


__all__ = ["attr_as"]
