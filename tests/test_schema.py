from __future__ import annotations

from typing import ClassVar
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
def event_id_fields():
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


@pytest.fixture
def jet_array_fields():
    return {
        "jet_pt_NOSYS": ak.Array([[10.0, 15.0], [], [12.5]]),
        "jet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "jet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),
        "jet_m": ak.Array([[125.0, 12.0], [], [83.0]]),
    }


def test_minimum(event_id_fields, jet_array_fields):
    array = {
        **event_id_fields,
        **jet_array_fields,
    }
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
    ).events()

    assert len(events) == 3
    assert events.ndim == 1
    assert events.jet.ndim == 2
    assert set(ak.fields(events.jet)) == {"pt", "pt_syst", "eta", "phi", "m"}
    assert set(ak.fields(events)) == {
        "lumiBlock",
        "runNumber",
        "actualInteractionsPerCrossing",
        "eventNumber",
        "mcEventWeights",
        "mcChannelNumber",
        "averageInteractionsPerCrossing",
        "dataTakingYear",
        "jet",
    }
    assert set(ak.fields(events.jet.pt_syst)) == {
        "NOSYS",
    }
    assert ak.all(events.jet.pt[0] == [10, 15])
    assert ak.all(events.jet.eta[1] == [])
    assert ak.all(events.jet.mass[2] == [83.0])
    assert isinstance(events.jet, JetArray)
    assert isinstance(events.jet[0, 0], JetRecord)


def test_minimum_no_event(jet_array_fields):
    array = {**jet_array_fields}

    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")

    with pytest.warns(
        RuntimeWarning,
        match=r"Missing event_ids",
    ):
        events = NanoEventsFactory.from_preloaded(
            src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
        ).events()

    assert len(events) == 3
    assert events.ndim == 1
    assert events.jet.ndim == 2
    assert set(ak.fields(events)) == {
        "jet",
    }
    assert set(ak.fields(events.jet)) == {"pt", "pt_syst", "eta", "phi", "m"}
    assert set(ak.fields(events.jet.pt_syst)) == {
        "NOSYS",
    }
    assert ak.all(events.jet.pt[0] == [10, 15])
    assert ak.all(events.jet.eta[1] == [])
    assert ak.all(events.jet.mass[2] == [83.0])
    assert isinstance(events.jet, JetArray)
    assert isinstance(events.jet[0, 0], JetRecord)


def test_easyjet_nosys_placement(event_id_fields):
    array = {
        **event_id_fields,
        "jet_NOSYS_pt": ak.Array([[10.0, 15.0], [], [12.5]]),
        "jet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "jet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),
        "jet_m": ak.Array([[125.0, 12.0], [], [83.0]]),
    }
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
    ).events()

    assert set(ak.fields(events.jet)) == {"pt", "pt_syst", "eta", "phi", "m"}
    assert set(ak.fields(events.jet.pt_syst)) == {
        "NOSYS",
    }


def test_undefined_mixin(event_id_fields):
    array = {
        **event_id_fields,
        "recojet_pt": ak.Array([[10.0, 15.0], [], [12.5]]),
        "recojet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "recojet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),
        "recojet_m": ak.Array([[125.0, 12.0], [], [83.0]]),
    }
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")

    with pytest.warns(
        RuntimeWarning,
        match=r"I found a collection with no defined mixin: 'recojet'. I will assume behavior: 'Jet'..*[mixin-undefined]",
    ):
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
            match=r"I found a collection with no defined mixin: 'recojet'. I will assume behavior: 'NanoCollection'..*[mixin-undefined]",
        ),
        attr_as(NtupleSchema, "identify_closest_behavior", False),
    ):
        events = NanoEventsFactory.from_preloaded(
            src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
        ).events()

    assert "recojet" in ak.fields(events)
    assert isinstance(events.recojet, NanoCollectionArray)
    assert isinstance(events.recojet[0, 0], NanoCollection)

    class MySchema(NtupleSchema):
        mixins: ClassVar[dict[str, str]] = {"recojet": "Jet", **NtupleSchema.mixins}

    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test"}, schemaclass=MySchema
    ).events()

    assert "recojet" in ak.fields(events)
    assert isinstance(events.recojet, JetArray)
    assert isinstance(events.recojet[0, 0], JetRecord)


def test_underscored_mixin(event_id_fields):
    array = {
        **event_id_fields,
        "recojet_antikt4PFlow_pt": ak.Array([[10.0, 15.0], [], [12.5]]),
        "recojet_antikt4PFlow_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "recojet_antikt10UFO_m": ak.Array([[], [10.0], []]),
        "recojet_antikt10UFO_eta": ak.Array([[], [1.2], []]),
    }
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")

    with (
        pytest.warns(
            RuntimeWarning,
            match=r"I found a collection with no defined mixin: 'recojet'. I will assume behavior: 'Jet'..*[mixin-undefined]",
        ),
        pytest.raises(
            TypeError, match=r"size of array \(\d+\) is less than size of form \(\d+\)"
        ),
    ):
        NanoEventsFactory.from_preloaded(
            src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
        ).events()

    class MySchema(NtupleSchema):
        mixins: ClassVar[dict[str, str]] = {
            "recojet_antikt4PFlow": "Jet",
            "recojet_antikt10UFO": "Jet",
            **NtupleSchema.mixins,
        }

    with (
        pytest.warns(
            RuntimeWarning,
            match=r"I identified a mixin that I did not automatically identify as a collection because it contained an underscore: 'recojet_antikt4PFlow'..*[mixin-underscore]",
        ),
        pytest.warns(
            RuntimeWarning,
            match=r"I identified a mixin that I did not automatically identify as a collection because it contained an underscore: 'recojet_antikt10UFO'..*[mixin-underscore]",
        ),
        pytest.warns(
            RuntimeWarning,
            match=r"I found a misidentified collection: 'recojet'. I will remove this from the known collections..*[collection-subset]",
        ),
    ):
        events = NanoEventsFactory.from_preloaded(
            src, metadata={"dataset": "test"}, schemaclass=MySchema
        ).events()

    assert len(events) == 3
    assert events.ndim == 1
    assert "recojet" not in ak.fields(events)
    assert "recojet_antikt4PFlow" in ak.fields(events)
    assert "recojet_antikt10UFO" in ak.fields(events)


def test_undefined_singleton(event_id_fields):
    array = {
        **event_id_fields,
        "singleton": ak.Array([[100], [200], [300]]),
    }
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")

    with pytest.warns(
        RuntimeWarning,
        match=r"I identified a branch that likely does not have any leaves: 'singleton'. I will treat this as a 'singleton..*[singleton-undefined]",
    ):
        events = NanoEventsFactory.from_preloaded(
            src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
        ).events()

    assert "singleton" in ak.fields(events)

    class MySchema(NtupleSchema):
        singletons: ClassVar[set[str]] = {
            "singleton",
        }

    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test"}, schemaclass=MySchema
    ).events()

    assert "singleton" in ak.fields(events)


def test_singleton_branch_with_NOSYS(event_id_fields):
    array = {
        **event_id_fields,
        "generatorWeight__NOSYS": ak.Array([[0.9], [1.1], [1.0]]),
    }
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")

    with pytest.raises(
        RuntimeError,
        match=r"One of the branches does not follow the assumed pattern for this schema. \[invalid-branch-name\]",
    ):
        NanoEventsFactory.from_preloaded(
            src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
        ).events()

    class MySchema(NtupleSchema):
        singletons: ClassVar[set[str]] = {"generatorWeight__NOSYS"}

    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test"}, schemaclass=MySchema
    ).events()

    assert len(events) == 3
    assert events.ndim == 1
    assert "generatorWeight__NOSYS" in ak.fields(events)
