from __future__ import annotations

from enum import IntEnum

import atlas_schema as ats


def test_enum_multiple_access():
    class Names(IntEnum, metaclass=ats.enums.MultipleEnumAccessMeta):
        Alice = 0
        Bob = 1
        Charlie = 2

    assert Names["Alice"] == Names.Alice
    assert Names["Bob"] == Names.Bob
    assert Names["Charlie"] == Names.Charlie
    assert Names["Alice", "Bob"] == [Names.Alice, Names.Bob]  # type:ignore[misc,comparison-overlap]
    assert Names["Bob", "Alice"] == [Names.Bob, Names.Alice]  # type:ignore[misc,comparison-overlap]
    assert Names["Charlie", "Alice", "Bob"] == [Names.Charlie, Names.Alice, Names.Bob]  # type:ignore[misc,comparison-overlap]
