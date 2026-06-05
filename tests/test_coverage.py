"""Tests targeting previously uncovered code paths to improve overall coverage."""

from __future__ import annotations

import importlib
import sys
import types
from uuid import uuid4

import awkward as ak
import coffea.nanoevents as _coffea_nanoevents
import coffea.nanoevents.transforms as _coffea_transforms
import pytest
from coffea.nanoevents import NanoEventsFactory
from coffea.nanoevents.mapping import SimplePreloadedColumnSource
from coffea.nanoevents.util import concat as _coffea_concat

from atlas_schema.schema import NtupleSchema


@pytest.fixture
def event_id_fields():
    return {
        "eventNumber": ak.Array([[1], [2], [3]]),
        "runNumber": ak.Array([[1], [1], [1]]),
        "lumiBlock": ak.Array([[1], [1], [1]]),
        "mcChannelNumber": ak.Array([[1], [1], [1]]),
        "actualInteractionsPerCrossing": ak.Array([[30], [30], [30]]),
        "averageInteractionsPerCrossing": ak.Array([[35], [35], [35]]),
        "dataTakingYear": ak.Array([[2018], [2018], [2018]]),
        "mcEventWeights": ak.Array([[1.0], [1.0], [1.0]]),
    }


def make_events(array: dict[str, ak.Array], schemaclass=NtupleSchema) -> ak.Array:
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    return NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test"}, schemaclass=schemaclass
    ).events()


# ── schema.py lines 194, 209 ──────────────────────────────────────────────────


def test_v1_classmethod_produces_events(event_id_fields):
    """NtupleSchema.v1 hits __init__ else-branch and can be used as a schemaclass."""
    events = make_events(event_id_fields, schemaclass=NtupleSchema.v1)
    assert len(events) == 3


# ── schema.py line 225 ───────────────────────────────────────────────────────


def test_apply_vector_fields_full_like_source_absent_silently_skips():
    """Silently skips full_like materialization when source field is absent."""
    schema = object.__new__(NtupleSchema)
    # no "pt" source field → full_like for Photon mass/charge is silently skipped
    content: dict[str, object] = {"eta": {}}
    schema._apply_vector_fields("Photon", content)
    assert "mass" not in content
    assert "charge" not in content


# ── schema.py lines 227-233 ───────────────────────────────────────────────────


def test_apply_vector_fields_full_like_target_already_present_warns():
    """Warns and skips when full_like target field already exists in collection."""
    schema = object.__new__(NtupleSchema)
    # "mass" and "charge" already in content; full_like_items wants to add both from "pt"
    content: dict[str, object] = {"pt": {}, "mass": {}, "charge": {}}
    with pytest.warns(RuntimeWarning, match=r"\[vector-field-exists\]"):
        schema._apply_vector_fields("Photon", content)
    # both fields must be kept, not overwritten
    assert "mass" in content
    assert "charge" in content


# ── schema.py lines 241-247 ───────────────────────────────────────────────────


def test_apply_vector_fields_rename_target_already_present_warns():
    """Warns and skips rename when target field already exists in collection."""
    schema = object.__new__(NtupleSchema)
    # rename_items says "m" → "mass"; "mass" already present
    content: dict[str, object] = {"m": {}, "mass": {}}
    with pytest.warns(RuntimeWarning, match=r"\[vector-field-exists\]"):
        schema._apply_vector_fields("Jet", content)
    # "m" must survive because the rename was skipped
    assert "m" in content


# ── schema.py line 251 ───────────────────────────────────────────────────────


def test_apply_vector_fields_alias_source_absent_silently_skips():
    """Silently skips alias when source field is absent."""
    schema = object.__new__(NtupleSchema)
    # no "met" source field → alias for MissingET rho is silently skipped
    content: dict[str, object] = {"phi": {}}
    schema._apply_vector_fields("MissingET", content)
    assert "rho" not in content


# ── schema.py lines 253-259 ───────────────────────────────────────────────────


def test_apply_vector_fields_alias_target_already_present_warns():
    """Warns and skips alias when target field already exists in collection."""
    schema = object.__new__(NtupleSchema)
    # alias_items says alias "met" → "rho"; "rho" already present
    content: dict[str, object] = {"met": {}, "rho": {}}
    with pytest.warns(RuntimeWarning, match=r"\[vector-field-exists\]"):
        schema._apply_vector_fields("MissingET", content)
    # "rho" must be kept, not overwritten
    assert "rho" in content


# ── schema.py lines 341, 347 ──────────────────────────────────────────────────


def test_error_missing_event_ids_raises():
    """error_missing_event_ids=True raises RuntimeError when event IDs are absent."""

    class ErrorSchema(NtupleSchema):
        error_missing_event_ids = True

    array = {"some_field_NOSYS": ak.Array([[1.0], [2.0], [3.0]])}
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    with pytest.raises(RuntimeError, match="There are missing event ID fields"):
        NanoEventsFactory.from_preloaded(
            src, metadata={"dataset": "test"}, schemaclass=ErrorSchema
        ).events()


# ── schema.py line 471 ───────────────────────────────────────────────────────


def test_systematic_loop_suggested_behavior_for_unknown_mixin(event_id_fields):
    """Systematic build loop calls suggested_behavior for collections not in mixins."""
    array = {
        **event_id_fields,
        # "recojet" is not in NtupleSchema.mixins → suggested_behavior is called
        "recojet_pt_NOSYS": ak.Array([[10.0], [20.0], []]),
        "recojet_pt_JET_EnergyScale__1up": ak.Array([[11.0], [21.0], []]),
        "recojet_eta": ak.Array([[0.5], [1.0], []]),
        "recojet_phi": ak.Array([[0.1], [0.5], []]),
        "recojet_m": ak.Array([[5.0], [6.0], []]),
    }
    with pytest.warns(RuntimeWarning, match=r"\[mixin-undefined\]"):
        events = make_events(array)
    syst = events.JET_EnergyScale__1up
    assert "recojet" in ak.fields(syst)


# ── methods.py line 22 ───────────────────────────────────────────────────────


def test_repr_classname_for_behavior_record(event_id_fields):
    """repr() on a behavior record instance returns the registered classname."""
    array = {
        **event_id_fields,
        "jet_pt_NOSYS": ak.Array([[10.0, 15.0], [], [12.5]]),
        "jet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "jet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),
        "jet_m": ak.Array([[5.0, 6.0], [], [7.0]]),
    }
    events = make_events(array)
    jet_record = events.jet[0, 0]
    assert repr(jet_record) == "Jet"


# ── methods.py line 44 ───────────────────────────────────────────────────────


def test_ntuple_events_scalar_nosys_getitem_returns_self(event_id_fields):
    """NtupleEvents scalar __getitem__ with 'NOSYS' returns the same object."""
    events = make_events(event_id_fields)
    single = events[0]
    assert single["NOSYS"] is single


# ── methods.py lines 59, 60 ──────────────────────────────────────────────────


def test_ntuple_events_scalar_systematic_names(event_id_fields):
    """NtupleEvents scalar systematic_names property includes 'NOSYS'."""
    events = make_events(event_id_fields)
    single = events[0]
    names = single.systematic_names
    assert "NOSYS" in names


# ── methods.py line 69 ───────────────────────────────────────────────────────


def test_ntuple_events_scalar_systematics_property(event_id_fields):
    """NtupleEvents scalar systematics property returns a list."""
    events = make_events(event_id_fields)
    single = events[0]
    systematics = single.systematics
    assert isinstance(systematics, list)


# ── methods.py line 170 ──────────────────────────────────────────────────────


def test_particle_passes_returns_bool_array_from_select_field(event_id_fields):
    """Particle.passes checks select_<name> == 1 and returns a boolean result."""
    array = {
        **event_id_fields,
        "jet_pt_NOSYS": ak.Array([[10.0, 15.0], [], [12.5]]),
        "jet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "jet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),
        "jet_m": ak.Array([[5.0, 6.0], [], [7.0]]),
        "jet_select_tight": ak.Array([[1, 0], [], [1]]),
    }
    events = make_events(array)
    passing = events.jet.passes("tight")
    assert ak.all(passing[0] == ak.Array([True, False]))
    assert ak.all(passing[2] == ak.Array([True]))


# ── transforms.py lines 16-52 ────────────────────────────────────────────────


@pytest.fixture
def old_coffea_transforms(monkeypatch):
    """Simulate old coffea that lacks full_like_from_content_form."""
    stub = types.ModuleType("coffea.nanoevents.transforms")
    for name in dir(_coffea_transforms):
        if "full_like" not in name and not name.startswith("__"):
            setattr(stub, name, getattr(_coffea_transforms, name))

    monkeypatch.setitem(sys.modules, "coffea.nanoevents.transforms", stub)
    monkeypatch.setattr(_coffea_nanoevents, "transforms", stub)
    monkeypatch.delitem(sys.modules, "atlas_schema.transforms", raising=False)
    return stub


def test_transforms_fallback_numpy_form(old_coffea_transforms):
    """Fallback full_like_from_content_form handles NumpyArray forms correctly."""
    t = importlib.import_module("atlas_schema.transforms")
    form = {
        "class": "NumpyArray",
        "form_key": "node0",
        "parameters": {"__doc__": "documentation to strip"},
    }
    result = t.full_like_from_content_form(form, 0.0)
    assert result["form_key"] == _coffea_concat("node0", "0.0,!full_like_from_content")
    assert "__doc__" not in result["parameters"]
    assert form["form_key"] == "node0"  # original not mutated


def test_transforms_fallback_listoffset_form(old_coffea_transforms):
    """Fallback full_like_from_content_form handles ListOffsetArray forms correctly."""
    t = importlib.import_module("atlas_schema.transforms")
    form = {
        "class": "ListOffsetArray",
        "offsets": "i64",
        "form_key": "node0",
        "parameters": {"__doc__": "outer doc"},
        "content": {
            "class": "NumpyArray",
            "form_key": "node1",
            "parameters": {"__doc__": "inner doc"},
        },
    }
    result = t.full_like_from_content_form(form, 1.5)
    expected_key = _coffea_concat("node0", "1.5,!full_like_from_content", "!content")
    assert result["content"]["form_key"] == expected_key
    assert "__doc__" not in result["parameters"]
    assert "__doc__" not in result["content"]["parameters"]
    assert form["form_key"] == "node0"  # original not mutated


def test_transforms_fallback_invalid_form_raises(old_coffea_transforms):
    """Fallback full_like_from_content_form raises RuntimeError for unsupported class."""
    t = importlib.import_module("atlas_schema.transforms")
    bad_form = {"class": "RecordArray", "form_key": "x", "parameters": {}}
    with pytest.raises(RuntimeError):
        t.full_like_from_content_form(bad_form, 0.0)


def test_transforms_fallback_runtime_function_fills_array(old_coffea_transforms):
    """Fallback full_like_from_content replaces stack top with a constant-filled copy."""
    t = importlib.import_module("atlas_schema.transforms")
    source = ak.Array([[1.0, 2.0], [], [3.0]])
    stack: list[object] = [source, 0.0]
    t.full_like_from_content(stack)
    result = stack[0]
    assert ak.all(result == 0.0)


def test_transforms_fallback_patched_into_coffea_module(old_coffea_transforms):
    """Fallback functions are registered onto the coffea transforms stub."""
    importlib.import_module("atlas_schema.transforms")
    assert callable(getattr(old_coffea_transforms, "full_like_from_content", None))
    assert callable(getattr(old_coffea_transforms, "full_like_from_content_form", None))
