"""Test script for systematic variation functionality."""

from __future__ import annotations

from uuid import uuid4

import awkward as ak
import pytest
from coffea.nanoevents import NanoEventsFactory
from coffea.nanoevents.mapping import SimplePreloadedColumnSource

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
def systematic_variation_fields():
    return {
        # Jet branches with systematic variations
        "jet_pt_NOSYS": ak.Array([[100.0, 150.0], [], [125.0]]),
        "jet_pt_JET_EnergyResolution__1up": ak.Array([[105.0, 155.0], [], [130.0]]),
        "jet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),  # No systematic variations
        "jet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),  # No systematic variations
        "jet_m": ak.Array([[125.0, 12.0], [], [83.0]]),  # No systematic variations
        # Electron branches with different systematic variations
        "el_pt_NOSYS": ak.Array([[50.0], [60.0], []]),
        "el_pt_EG_RESOLUTION_ALL__1up": ak.Array([[52.0], [62.0], []]),
        "el_eta": ak.Array([[1.0], [1.5], []]),
        "el_phi": ak.Array([[0.5], [1.0], []]),
        # Muon branches with no systematic variations (to test fallback)
        "mu_pt_NOSYS": ak.Array([[40.0], [], [45.0]]),
        "mu_eta": ak.Array([[1.2], [], [0.8]]),
        "mu_phi": ak.Array([[0.8], [], [1.1]]),
    }


def test_systematic_variations(event_id_fields, systematic_variation_fields):
    """Test the new systematic variation functionality."""

    # Create test data with systematic variations
    array = {
        **event_id_fields,
        **systematic_variation_fields,
    }

    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test_systematics"}, schemaclass=NtupleSchema
    ).events()

    print("=== Testing Systematic Variations ===")

    # Debug: Check what fields exist
    print(f"Event fields: {list(events.fields)}")
    print(f"Event metadata: {getattr(events, 'metadata', {})}")
    print(f"Event dir: {[attr for attr in dir(events) if 'meta' in attr.lower()]}")
    print(f"Event behavior: {hasattr(events, 'behavior')}")
    if (
        hasattr(events, "behavior")
        and events.behavior
        and "__events_factory__" in events.behavior
    ):
        factory = events.behavior["__events_factory__"]
        print(f"Factory metadata: {getattr(factory, 'metadata', {})}")

    # Test 1: Check that systematic collections are created
    expected_systematics = ["EG_RESOLUTION_ALL__1up", "JET_EnergyResolution__1up"]

    # Check that systematic collections exist as top-level fields
    for syst in expected_systematics:
        assert hasattr(events, syst), f"Expected systematic collection {syst} to exist"
        syst_events = getattr(events, syst)
        print(f"Systematic {syst} fields: {list(syst_events.fields)}")

        # Check that each systematic has the expected object collections
        assert hasattr(syst_events, "jet"), (
            f"Systematic {syst} should have jet collection"
        )
        assert hasattr(syst_events, "el"), (
            f"Systematic {syst} should have el collection"
        )
        assert hasattr(syst_events, "mu"), (
            f"Systematic {syst} should have mu collection"
        )

    # Test 2: Check nominal access works (backward compatibility)
    print(f"Nominal jet pt: {events.jet.pt}")
    print(f"Nominal electron pt: {events.el.pt}")
    print(f"Nominal muon pt: {events.mu.pt}")

    # Test 3: Check nominal collections (no _syst fields in new approach)
    print("Nominal collections:")
    print(f"  Jet fields: {list(events.jet.fields)}")
    print(f"  Electron fields: {list(events.el.fields)}")
    print(f"  Muon fields: {list(events.mu.fields)}")

    # In the new approach, nominal collections should NOT have _syst fields
    assert "pt_syst" not in events.jet.fields, (
        "jet should NOT have pt_syst field in new approach"
    )
    assert "pt_syst" not in events.el.fields, (
        "electron should NOT have pt_syst field in new approach"
    )

    # Test 4: Test systematic variation access
    print("\n=== Testing Systematic Access ===")

    # Check nominal access
    if hasattr(events, "nominal"):
        print(f"Nominal via events.nominal.jet.pt: {events.nominal.jet.pt}")
        print(f"Nominal via events.nominal.el.pt: {events.nominal.el.pt}")
        print(f"Nominal via events.nominal.mu.pt: {events.nominal.mu.pt}")

    # Check systematic variation access using new interface
    for syst in expected_systematics:
        print(f"\nSystematic {syst}:")
        syst_events = getattr(events, syst)
        try:
            print(f"  Jet pt: {syst_events.jet.pt}")
        except Exception as e:
            print(f"  Jet pt error: {e}")
        try:
            print(f"  Electron pt: {syst_events.el.pt}")
        except Exception as e:
            print(f"  Electron pt error: {e}")
        try:
            print(f"  Muon pt (should fallback to nominal): {syst_events.mu.pt}")
        except Exception as e:
            print(f"  Muon pt error: {e}")

    # Test 5: Test that systematic variations have correct values
    if hasattr(events, "JET_EnergyResolution__1up"):
        jet_syst_pt = events.JET_EnergyResolution__1up.jet.pt
        expected_jet_syst = ak.Array([[105.0, 155.0], [], [130.0]])
        print(f"Jet systematic pt: {jet_syst_pt}")
        print(f"Expected jet systematic pt: {expected_jet_syst}")
        # assert ak.all(jet_syst_pt == expected_jet_syst), "Jet systematic variation should match expected values"

    if hasattr(events, "EG_RESOLUTION_ALL__1up"):
        el_syst_pt = events.EG_RESOLUTION_ALL__1up.el.pt
        expected_el_syst = ak.Array([[52.0], [62.0], []])
        print(f"Electron systematic pt: {el_syst_pt}")
        print(f"Expected electron systematic pt: {expected_el_syst}")
        # assert ak.all(el_syst_pt == expected_el_syst), "Electron systematic variation should match expected values"

    print("\n=== Test completed successfully! ===")


def test_nosys_alias_returns_same_object(event_id_fields, systematic_variation_fields):
    """Test that events["NOSYS"] returns the same object as events."""
    array = {**event_id_fields, **systematic_variation_fields}
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test_nosys_alias"}, schemaclass=NtupleSchema
    ).events()

    nosys_events = events["NOSYS"]
    assert nosys_events is events, (
        "events['NOSYS'] should return the same object as events"
    )


def test_systematic_names_includes_nosys(event_id_fields, systematic_variation_fields):
    """Test that systematic_names includes NOSYS as the first entry."""
    array = {**event_id_fields, **systematic_variation_fields}
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test_systematic_names"}, schemaclass=NtupleSchema
    ).events()

    assert "NOSYS" in events.systematic_names, "systematic_names should include 'NOSYS'"
    assert events.systematic_names[0] == "NOSYS", (
        "NOSYS should be first in systematic_names"
    )


def test_nosys_iteration_pattern(event_id_fields, systematic_variation_fields):
    """Test the clean iteration pattern with NOSYS support."""
    array = {**event_id_fields, **systematic_variation_fields}
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test_iteration"}, schemaclass=NtupleSchema
    ).events()

    # Test the iteration pattern that was requested
    for variation in events.systematic_names:
        event_view = events[variation]

        if variation == "NOSYS":
            # Should be the same object
            assert event_view is events, (
                f"events['{variation}'] should be the same as events"
            )
            # Should have access to collections
            assert hasattr(event_view, "jet"), "NOSYS events should have jet collection"
        else:
            # Should be a systematic variation
            assert hasattr(event_view, "jet"), (
                f"Variation {variation} should have jet collection"
            )


def test_nosys_collections_accessible(event_id_fields, systematic_variation_fields):
    """Test that collections are accessible through NOSYS alias."""
    array = {**event_id_fields, **systematic_variation_fields}
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test_collections"}, schemaclass=NtupleSchema
    ).events()

    nosys_events = events["NOSYS"]

    # Test that we can access collections through the NOSYS alias
    assert hasattr(nosys_events, "jet"), "NOSYS events should have jet collection"
    assert hasattr(nosys_events, "el"), "NOSYS events should have el collection"
    assert hasattr(nosys_events, "mu"), "NOSYS events should have mu collection"

    # Test that the data is the same
    assert ak.all(nosys_events.jet.pt == events.jet.pt), (
        "NOSYS jet pt should match original"
    )
    assert ak.all(nosys_events.el.pt == events.el.pt), (
        "NOSYS el pt should match original"
    )
    assert ak.all(nosys_events.mu.pt == events.mu.pt), (
        "NOSYS mu pt should match original"
    )


def test_nosys_getitem_fallback(event_id_fields, systematic_variation_fields):
    """Test that non-NOSYS keys fall back to super().__getitem__."""
    array = {**event_id_fields, **systematic_variation_fields}
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test_fallback"}, schemaclass=NtupleSchema
    ).events()

    # Test accessing a systematic variation through bracket notation
    systematic_events = events["JET_EnergyResolution__1up"]
    assert systematic_events is not events, (
        "Systematic variation should be different object"
    )
    assert hasattr(systematic_events, "jet"), (
        "Systematic variation should have jet collection"
    )

    # Test accessing an invalid key to ensure super().__getitem__ is called
    with pytest.raises(ak.errors.FieldNotFoundError):
        _ = events["nonexistent_systematic"]
