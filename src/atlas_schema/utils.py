from __future__ import annotations

from enum import Enum
from typing import TypeVar, Union, cast

import awkward as ak
import dask_awkward as dak

Array = TypeVar("Array", bound=Union[dak.Array, ak.Array])
_E = TypeVar("_E", bound=Enum)


def isin(haystack: Array, needles: dak.Array | ak.Array, axis: int = -1) -> Array:
    """
    Find needles in haystack. Similar in API as :func:`numpy.isin`.

    Calculates `haystack in needles`, broadcasting over *haystack elements only*. Returns a boolean array of the same shape as *haystack* that is `True` where an element of *element* is in *needles* and `False` otherwise.

    This works by first transforming *needles* to an array with one more
    dimension than the *haystack*, placing the *needles* at *axis*, and then doing a
    comparison.

    Args:
        haystack (dak.Array or ak.Array): haystack of values.
        needles (dak.Array or ak.Array): one-dimensional set of needles to find in haystack.
        axis (int): the axis along which the comparison is performed

    Returns:
        dak.Array or ak.Array: result of comparison for needles in haystack

    Example:
        >>> import awkward as ak
        >>> import atlas_schema as ats
        >>> truth_origins = ak.Array([[1, 2, 3], [4], [5, 6, 7], [1]])
        >>> prompt_origins = ak.Array([1, 2, 7])
        >>> ats.isin(truth_origins, prompt_origins).to_list()
        [[True, True, False], [False], [False, False, True], [True]]
    """
    assert needles.ndim == 1, "Needles must be one-dimensional"
    assert axis >= -1, "axis must be -1 or positive-valued"
    assert axis < haystack.ndim + 1, "axis too large for the haystack"

    # First, build up the transformation, with slice(None) indicating where to stick the needles
    reshaper: list[None | slice] = [None] * haystack.ndim
    axis = haystack.ndim if axis == -1 else axis
    reshaper.insert(axis, slice(None))

    # Note: reshaper needs to be a tuple for indexing purposes
    return cast(Array, ak.any(haystack == needles[tuple(reshaper)], axis=-1))
