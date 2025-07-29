from __future__ import annotations

import awkward as ak

import atlas_schema as ats


def test_isin():
    array = ak.Array([[1, 2, 3], [4], [5, 6, 7], [1]])
    test = ak.Array([1, 2, 7])
    result = ak.Array([[True, True, False], [False], [False, False, True], [True]])
    assert ak.all(ats.isin(array, test) == result)


def test_isin_diffaxis():
    array = ak.Array([[1, 2, 3], [4], [5, 6, 7], [1]])
    test = ak.Array([1])
    result = ak.Array([[True, False, False], [False], [False, False, False], [True]])
    assert ak.all(ats.isin(array, test) == result)


def test_isin_moredimensions():
    array = ak.Array([[[1], [2], [3]], [[4]], [[5], [6], [7]], [[1]]])
    test = ak.Array([1, 2, 7])
    result = ak.Array(
        [[[True], [True], [False]], [[False]], [[False], [False], [True]], [[True]]]
    )
    assert ak.all(ats.isin(array, test) == result)
