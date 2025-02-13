from __future__ import annotations

import awkward as ak
import dask_awkward as dak

import atlas_schema as ats


def test_isin():
    array = ak.Array([[1, 2, 3], [4], [5, 6, 7], [1]])
    array_dask = dak.from_awkward(array, npartitions=2)
    test = ak.Array([1, 2, 7])
    result = ak.Array([[True, True, False], [False], [False, False, True], [True]])
    assert ak.all(ats.isin(array, test) == result)
    assert ak.all(ats.isin(array_dask, test).compute() == result)
