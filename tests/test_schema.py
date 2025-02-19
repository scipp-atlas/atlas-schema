from __future__ import annotations

from uuid import uuid4

import awkward as ak
import pytest
from coffea.nanoevents import NanoEventsFactory
from coffea.nanoevents.mapping import SimplePreloadedColumnSource
from coffea.nanoevents.methods.base import NanoCollection, NanoCollectionArray
from helpers import attr_as

from atlas_schema.methods import JetArray, JetRecord  # type:ignore[attr-defined]
from atlas_schema.schema import NtupleSchema


@pytest.fixture
def minimum_required_fields():
    return {
        "eventNumber": ak.Array([[123456789], [123456790], [123456791]]),
        "runNumber": ak.Array([[654321], [654321], [654321]]),
        "lumiBlock": ak.Array([[12390123], [12390123], [12390123]]),
        "mcChannelNumber": ak.Array([[654321], [654321], [654321]]),
        "actualInteractionsPerCrossing": ak.Array([[30], [30], [30]]),
        "averageInteractionsPerCrossing": ak.Array([[35], [35], [35]]),
        "dataTakingYear": ak.Array([[2018], [2018], [2018]]),
        "mcEventWeights": ak.Array([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]),
    }


def test_simple_load(minimum_required_fields):
    array = {
        **minimum_required_fields,
        "jet_pt": ak.Array([[10.0, 15.0], [], [12.5]]),
        "jet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "jet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),
    }
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
    ).events()

    assert len(events) == 3
    assert events.ndim == 1
    assert events.jet.ndim == 2
    assert ak.all(events.jet.pt[0] == [10, 15])
    assert ak.all(events.jet.eta[1] == [])
    assert isinstance(events.jet, JetArray)
    assert isinstance(events.jet[0, 0], JetRecord)


def test_undefined_mixin(minimum_required_fields):
    array = {
        **minimum_required_fields,
        "recojet_pt": ak.Array([[10.0, 15.0], [], [12.5]]),
        "recojet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "recojet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),
    }
    with pytest.warns(
        RuntimeWarning,
        match="I found a collection with no defined mixin: 'recojet'. I will assume behavior: 'Jet'.",
    ):
        src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
        events = NanoEventsFactory.from_preloaded(
            src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
        ).events()

        assert len(events) == 3
        assert events.ndim == 1
        assert "recojet" in ak.fields(events)
        assert isinstance(events.recojet, JetArray)
        assert isinstance(events.recojet[0, 0], JetRecord)

    with (
        pytest.warns(
            RuntimeWarning,
            match="I found a collection with no defined mixin: 'recojet'. I will assume behavior: 'NanoCollection'.",
        ),
        attr_as(NtupleSchema, "identify_closest_behavior", False),
    ):
        src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
        events = NanoEventsFactory.from_preloaded(
            src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
        ).events()

        assert "recojet" in ak.fields(events)
        assert isinstance(events.recojet, NanoCollectionArray)
        assert isinstance(events.recojet[0, 0], NanoCollection)
