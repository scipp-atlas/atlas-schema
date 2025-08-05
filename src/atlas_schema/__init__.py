"""
Copyright (c) 2024 Giordon Stark. All rights reserved.

atlas_schema: Collection of utilities and helper functions for HEP ATLAS analysers
"""

from __future__ import annotations

import sys
import warnings
from typing import Any

from dask.sizeof import sizeof

from atlas_schema._version import version as __version__
from atlas_schema.enums import ParticleOrigin, PhotonID
from atlas_schema.utils import isin

warnings.filterwarnings("ignore", module="coffea.*")


@sizeof.register(dict)  # type: ignore[misc]
def custom_sizeof_python_dict(the_dict: dict[Any, Any]) -> int:
    """
    Resolve issues with dask recursively crashing when computing the `sizeof` certain objects.

    Reference: https://iris-hep.slack.com/archives/CFZ4Z2Q2H/p1743028866008279?thread_ts=1742946320.950709&cid=CFZ4Z2Q2H
    Credit: Yizhou Cai
    """
    try:
        total_size = sys.getsizeof(the_dict)

        for key, value in the_dict.items():
            try:
                total_size += sizeof(key)
            except Exception:
                total_size += sys.getsizeof(key)

            try:
                total_size += sizeof(value)
            except Exception:
                total_size += sys.getsizeof(value)

        total_size -= 2 * sys.getsizeof([])

        return total_size

    except Exception as e:
        warnings.warn(
            f"Error calculating size of dict: {e}",
            RuntimeWarning,
            stacklevel=2,
        )
        return int(1e6)


__all__ = ["ParticleOrigin", "PhotonID", "__version__", "isin"]
