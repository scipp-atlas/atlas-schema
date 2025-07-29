from __future__ import annotations

from enum import Enum
from typing import TypeVar, cast

import awkward as ak

Array = TypeVar("Array", bound=ak.Array)
_E = TypeVar("_E", bound=Enum)


def isin(element: Array, test_elements: ak.Array, axis: int = -1) -> Array:
    """
    Find test_elements in element. Similar in API as :func:`numpy.isin`.

    Calculates `element in test_elements`, broadcasting over *element elements only*. Returns a boolean array of the same shape as *element* that is `True` where an element of *element* is in *test_elements* and `False` otherwise.

    This works by first transforming *test_elements* to an array with one more
    dimension than the *element*, placing the *test_elements* at *axis*, and then doing a
    comparison.

    Args:
        element (ak.Array): input array of values.
        test_elements (ak.Array): one-dimensional set of values against which to test each value of *element*.
        axis (int): the axis along which the comparison is performed

    Returns:
        ak.Array: result of comparison for test_elements in *element*

    Example:
        >>> import awkward as ak
        >>> import atlas_schema as ats
        >>> truth_origins = ak.Array([[1, 2, 3], [4], [5, 6, 7], [1]])
        >>> prompt_origins = ak.Array([1, 2, 7])
        >>> ats.isin(truth_origins, prompt_origins).to_list()
        [[True, True, False], [False], [False, False, True], [True]]
    """
    assert test_elements.ndim == 1, "test_elements must be one-dimensional"
    assert axis >= -1, "axis must be -1 or positive-valued"
    assert axis < element.ndim + 1, "axis too large for the element"

    # First, build up the transformation, with slice(None) indicating where to stick the test_elements
    reshaper: list[None | slice] = [None] * element.ndim
    axis = element.ndim if axis == -1 else axis
    reshaper.insert(axis, slice(None))

    # Note: reshaper needs to be a tuple for indexing purposes
    return cast(Array, ak.any(element == test_elements[tuple(reshaper)], axis=-1))
