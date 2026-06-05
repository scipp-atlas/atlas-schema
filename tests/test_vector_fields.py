"""Tests that vector coordinate fields are materialized as real awkward fields."""

from __future__ import annotations

import contextlib
from uuid import uuid4

import awkward as ak
import numpy as np
import particle
import pytest
from coffea.nanoevents import NanoEventsFactory
from coffea.nanoevents.mapping import SimplePreloadedColumnSource

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


def make_events(array: dict[str, ak.Array]) -> ak.Array:
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    return NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
    ).events()


# ---------------------------------------------------------------------------
# Electron
# ---------------------------------------------------------------------------


def test_electron_mass_field_exists(event_id_fields):
    array = {
        **event_id_fields,
        "el_pt_NOSYS": ak.Array([[50.0, 60.0], [], [70.0]]),
        "el_eta": ak.Array([[0.5, 1.0], [], [1.2]]),
        "el_phi": ak.Array([[0.1, 3.0], [], [0.8]]),
    }
    events = make_events(array)
    assert "mass" in ak.fields(events.el)


def test_electron_mass_value_is_electron_mass(event_id_fields):
    array = {
        **event_id_fields,
        "el_pt_NOSYS": ak.Array([[50.0, 60.0], [], [70.0]]),
        "el_eta": ak.Array([[0.5, 1.0], [], [1.2]]),
        "el_phi": ak.Array([[0.1, 3.0], [], [0.8]]),
    }
    events = make_events(array)
    expected = float(particle.literals.e_minus.mass)
    assert ak.all(np.abs(ak.to_numpy(ak.flatten(events.el.mass)) - expected) < 1e-3)


def test_electron_vector_sum_mass(event_id_fields):
    """(e1 + e2).mass is correct with real mass field — not zero/garbage."""
    array = {
        **event_id_fields,
        "el_pt_NOSYS": ak.Array([[50.0, 60.0], [], [70.0]]),
        "el_eta": ak.Array([[0.5, 1.0], [], [1.2]]),
        "el_phi": ak.Array([[0.1, 3.0], [], [0.8]]),
    }
    events = make_events(array)
    # Use scalar indexing into event 0 which has two electrons
    e1 = events.el[0, 0]
    e2 = events.el[0, 1]
    pair_mass = (e1 + e2).mass
    assert pair_mass > 0


# ---------------------------------------------------------------------------
# Muon
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("collection", "pt_field", "eta_field", "phi_field", "expected_mass_attr"),
    [
        (
            "mu",
            "mu_pt_NOSYS",
            "mu_eta",
            "mu_phi",
            "mu_minus",
        ),
        (
            "tau",
            "tau_pt_NOSYS",
            "tau_eta",
            "tau_phi",
            "tau_minus",
        ),
    ],
)
def test_lepton_mass_field_exists_and_correct(
    event_id_fields, collection, pt_field, eta_field, phi_field, expected_mass_attr
):
    array = {
        **event_id_fields,
        pt_field: ak.Array([[40.0, 45.0], [], [50.0]]),
        eta_field: ak.Array([[0.5, 1.0], [], [1.2]]),
        phi_field: ak.Array([[0.1, 3.0], [], [0.8]]),
    }
    with (
        pytest.warns(RuntimeWarning, match=r"\[mixin-undefined\]")
        if collection not in NtupleSchema.mixins
        else contextlib.nullcontext()
    ):
        events = make_events(array)
    coll = getattr(events, collection)
    assert "mass" in ak.fields(coll)
    expected = float(getattr(particle.literals, expected_mass_attr).mass)
    assert ak.all(np.abs(ak.to_numpy(ak.flatten(coll.mass)) - expected) < 1e-3)


# ---------------------------------------------------------------------------
# Photon
# ---------------------------------------------------------------------------


def test_photon_mass_field_is_zero(event_id_fields):
    array = {
        **event_id_fields,
        "ph_pt_NOSYS": ak.Array([[80.0, 90.0], [], [100.0]]),
        "ph_eta": ak.Array([[0.5, 1.0], [], [1.2]]),
        "ph_phi": ak.Array([[0.1, 3.0], [], [0.8]]),
    }
    events = make_events(array)
    assert "mass" in ak.fields(events.ph)
    assert ak.all(events.ph.mass == 0.0)


def test_photon_charge_field_is_zero(event_id_fields):
    array = {
        **event_id_fields,
        "ph_pt_NOSYS": ak.Array([[80.0, 90.0], [], [100.0]]),
        "ph_eta": ak.Array([[0.5, 1.0], [], [1.2]]),
        "ph_phi": ak.Array([[0.1, 3.0], [], [0.8]]),
    }
    events = make_events(array)
    assert "charge" in ak.fields(events.ph)
    assert ak.all(events.ph.charge == 0.0)


def test_photon_vector_sum_mass(event_id_fields):
    """Diphoton (ph + ph).mass is the massless invariant mass."""
    array = {
        **event_id_fields,
        "ph_pt_NOSYS": ak.Array([[80.0, 90.0], [], [100.0]]),
        "ph_eta": ak.Array([[0.5, 1.0], [], [1.2]]),
        "ph_phi": ak.Array([[0.1, 3.0], [], [0.8]]),
    }
    events = make_events(array)
    # Use scalar indexing into event 0 which has two photons
    ph1 = events.ph[0, 0]
    ph2 = events.ph[0, 1]
    pair_mass = (ph1 + ph2).mass
    assert pair_mass > 0


# ---------------------------------------------------------------------------
# Jet
# ---------------------------------------------------------------------------


def test_jet_mass_field_exists(event_id_fields):
    array = {
        **event_id_fields,
        "jet_pt_NOSYS": ak.Array([[10.0, 15.0], [], [12.5]]),
        "jet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "jet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),
        "jet_m": ak.Array([[125.0, 12.0], [], [83.0]]),
    }
    events = make_events(array)
    assert "mass" in ak.fields(events.jet)


def test_jet_mass_values_match_input(event_id_fields):
    array = {
        **event_id_fields,
        "jet_pt_NOSYS": ak.Array([[10.0, 15.0], [], [12.5]]),
        "jet_eta": ak.Array([[0.5, 1.8], [], [1.2]]),
        "jet_phi": ak.Array([[0.01, 1.2], [], [0.8]]),
        "jet_m": ak.Array([[125.0, 12.0], [], [83.0]]),
    }
    events = make_events(array)
    assert ak.all(events.jet.mass[0] == [125.0, 12.0])
    assert ak.all(events.jet.mass[2] == [83.0])


# ---------------------------------------------------------------------------
# MissingET
# ---------------------------------------------------------------------------


def test_met_rho_field_exists(event_id_fields):
    array = {
        **event_id_fields,
        "met_met_NOSYS": ak.Array([[120.0], [80.0], [200.0]]),
        "met_phi": ak.Array([[0.5], [1.2], [2.1]]),
    }
    events = make_events(array)
    assert "rho" in ak.fields(events.met)


def test_met_rho_equals_met_magnitude(event_id_fields):
    array = {
        **event_id_fields,
        "met_met_NOSYS": ak.Array([[120.0], [80.0], [200.0]]),
        "met_phi": ak.Array([[0.5], [1.2], [2.1]]),
    }
    events = make_events(array)
    assert ak.all(events.met.rho == events.met.met)


def test_met_vector_pt_and_r_from_rho(event_id_fields):
    """After materializing rho, vector's .pt and .r both resolve to rho."""
    array = {
        **event_id_fields,
        "met_met_NOSYS": ak.Array([[120.0], [80.0], [200.0]]),
        "met_phi": ak.Array([[0.5], [1.2], [2.1]]),
    }
    events = make_events(array)
    assert ak.all(events.met.pt == events.met.rho)
    assert ak.all(events.met.r == events.met.rho)


# ---------------------------------------------------------------------------
# Systematic: materialized fields survive both build paths
# ---------------------------------------------------------------------------


def test_systematic_collection_has_materialized_fields():
    """Materialized vector fields must exist in systematic (non-NOSYS) collections."""
    array = {
        "eventNumber": ak.Array([[1], [2], [3]]),
        "runNumber": ak.Array([[1], [1], [1]]),
        "lumiBlock": ak.Array([[1], [1], [1]]),
        "mcChannelNumber": ak.Array([[1], [1], [1]]),
        "actualInteractionsPerCrossing": ak.Array([[30], [30], [30]]),
        "averageInteractionsPerCrossing": ak.Array([[35], [35], [35]]),
        "dataTakingYear": ak.Array([[2018], [2018], [2018]]),
        "mcEventWeights": ak.Array([[1.0], [1.0], [1.0]]),
        # Electron with a systematic variation
        "el_pt_NOSYS": ak.Array([[50.0], [60.0], []]),
        "el_pt_EG_RESOLUTION_ALL__1up": ak.Array([[52.0], [62.0], []]),
        "el_eta": ak.Array([[1.0], [1.5], []]),
        "el_phi": ak.Array([[0.5], [1.0], []]),
        # MET with no systematic (tests nominal-reuse path)
        "met_met_NOSYS": ak.Array([[120.0], [80.0], [200.0]]),
        "met_phi": ak.Array([[0.5], [1.2], [2.1]]),
    }
    src = SimplePreloadedColumnSource(array, uuid4(), 3, object_path="/Events")
    events = NanoEventsFactory.from_preloaded(
        src, metadata={"dataset": "test"}, schemaclass=NtupleSchema
    ).events()

    syst = events.EG_RESOLUTION_ALL__1up

    # Rebuilt systematic collection must have mass
    assert "mass" in ak.fields(syst.el), "el.mass must be materialized in systematic"
    # MET uses nominal-reuse path; rho must still be present
    assert "rho" in ak.fields(syst.met), (
        "met.rho must be present via nominal-reuse path"
    )
