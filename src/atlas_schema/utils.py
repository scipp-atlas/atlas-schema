from __future__ import annotations

from typing import TypeVar, Union, cast

import awkward as ak
import dask_awkward as dak

Array = TypeVar("Array", bound=Union[dak.Array, ak.Array])


def isin(haystack: Array, needles: dak.Array | ak.Array) -> Array:
    """
    Find needles in haystack.

    This works by first transforming haystack to Array[N*M*K] and then doing a comparison.

    Args:
        haystack (dak.Array[N*M] or ak.Array[N*M]): three-dimensional haystack of values.
        needles (dak.Array[K] or ak.Array[K]): one-dimensional set of needles to find in haystack.

    Returns:
        mask (dak.Array[N*M] or ak.Array[N*M]): result of comparison for needles in haystack
    """
    # Note: the colon indicates where the other dimension is for readability
    return cast(Array, ak.any(haystack == needles[None, None, :], axis=-1))
