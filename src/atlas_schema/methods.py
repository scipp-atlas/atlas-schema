"""Mixins for the Ntuple schema"""

from __future__ import annotations

from functools import reduce
from operator import ior

import awkward
import particle
from coffea.nanoevents.methods import base, candidate, vector

from atlas_schema.enums import PhotonID
from atlas_schema.typing_compat import Behavior

behavior: Behavior = {}
behavior.update(base.behavior)
# vector behavior is included in candidate behavior
behavior.update(candidate.behavior)


def _set_repr_name(classname):
    def namefcn(_self):
        return classname

    behavior[("__typestr__", classname)] = classname[0].lower() + classname[1:]
    behavior[classname].__repr__ = namefcn


class NtupleEvents(behavior["NanoEvents"]):  # type: ignore[misc, valid-type, name-defined]
    """Individual systematic variation of events."""

    def __repr__(self):
        return f"<event {getattr(self, 'runNumber', '??')}:{getattr(self, 'eventNumber', '??')}:{getattr(self, 'mcChannelNumber', '??')}>"

    def __getitem__(self, key):
        """Support accessing systematic variations via bracket notation.

        Args:
            key: The systematic variation name. "NOSYS" returns the nominal events.

        Returns:
            The requested systematic variation or nominal events for "NOSYS".
        """
        if key == "NOSYS":
            return self
        return super().__getitem__(key)

    @property
    def systematic(self):
        """Get the systematic variation name for this event collection."""
        return "nominal"

    @property
    def systematic_names(self):
        """Get all systematic variations available in this event collection.

        Returns a list of systematic variation names, including 'NOSYS' for nominal.
        """
        # Get systematics from metadata stored during schema building
        systematics = self.metadata.get("systematics", [])
        return ["NOSYS", *systematics]

    @property
    def systematics(self):
        """Get all systematic variations available in this event collection.

        Returns a list of systematic variation names, excluding 'nominal'.
        """
        # Get systematics from metadata stored during schema building
        return [getattr(self, systematic) for systematic in self.systematic_names]


behavior["NtupleEvents"] = NtupleEvents


class NtupleEventsArray(behavior[("*", "NanoEvents")]):  # type: ignore[misc, valid-type, name-defined]
    """Collection of NtupleEvents objects, one for each systematic variation."""

    def __getitem__(self, key):
        """Support accessing systematic variations via bracket notation.

        Args:
            key: The systematic variation name. "NOSYS" returns the nominal events.

        Returns:
            The requested systematic variation or nominal events for "NOSYS".
        """
        if key == "NOSYS":
            return self
        return super().__getitem__(key)

    @property
    def systematic_names(self):
        """Get all systematic variations available in this event collection.

        Returns a list of systematic variation names, including 'NOSYS' for nominal.
        """
        # Get systematics from metadata stored during schema building
        systematics = self.metadata.get("systematics", [])
        return ["NOSYS", *systematics]

    @property
    def systematics(self):
        """Get all systematic variations available in this event collection.

        Returns a list of systematic variation names, excluding 'nominal'.
        """
        # Get systematics from metadata stored during schema building
        return [getattr(self, systematic) for systematic in self.systematic_names]


behavior[("*", "NtupleEvents")] = NtupleEventsArray


@awkward.mixin_class(behavior)
class Systematic(base.NanoCollection, base.Systematic):
    """Base class for systematic variations."""

    @property
    def metadata(self):
        """Arbitrary metadata"""
        return self.layout.purelist_parameter("metadata")  # pylint: disable=no-member

    @property
    def systematic(self):
        """Get the systematic variation name for this event collection."""
        return self.metadata["systematic"]

    def __repr__(self):
        return f"<event {self.systematic}>"

    def _build_variations(self, _name, what, varying_function):
        """Build systematic variations - base implementation."""
        return varying_function(self, what)

    def describe_variations(self):
        """Return list of variation names."""
        return []

    def explodes_how(self):
        """Describe how systematic uncertainty should be evaluated."""
        return "independent"


_set_repr_name("Systematic")


@awkward.mixin_class(behavior)
class Weight(base.NanoCollection, base.Systematic):
    """Weight systematic variation."""

    def _build_variations(self, _name, what, varying_function):
        """Build weight variations."""
        return varying_function(self, what)

    def describe_variations(self):
        """Return list of weight variation names."""
        return []

    def explodes_how(self):
        """Weight variations are independent."""
        return "independent"


_set_repr_name("Weight")


@awkward.mixin_class(behavior)
class Pass(base.NanoCollection, base.Systematic):
    """Pass systematic variation."""

    def _build_variations(self, _name, what, varying_function):
        """Build pass variations."""
        return varying_function(self, what)

    def describe_variations(self):
        """Return list of pass variation names."""
        return []

    def explodes_how(self):
        """Pass variations are independent."""
        return "independent"


_set_repr_name("Pass")

behavior.update(
    awkward._util.copy_behaviors("PtEtaPhiMLorentzVector", "Particle", behavior)  # pylint: disable=protected-access
)


@awkward.mixin_class(behavior)
class Particle(vector.PtEtaPhiMLorentzVector):
    """Generic particle collection that has Lorentz vector properties

    Also handles the following additional branches:
    - '{obj}_select'
    """

    def passes(self, name):
        return self[f"select_{name}"] == 1

    # NB: fields with the name 'pt' take precedence over this
    # @dask_property
    # def pt(self):
    #     print('inside non-dask prop')
    #     return self["pt_NOSYS"]

    # @pt.dask
    # def pt(self, dask_array):
    #     branch = 'pt'
    #     print('inside dask prop')
    #     variation = dask_array._events().metadata.get("systematic", "NOSYS")
    #     with contextlib.suppress(Exception):
    #         return dask_array[f"{branch}_{variation}"]

    #     if variation != "NOSYS":
    #         with contextlib.suppress(Exception):
    #             return dask_array[f"{branch}_NOSYS"]

    #     return dask_array[branch]


_set_repr_name("Particle")

ParticleArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
ParticleArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
ParticleArray.ProjectionClass4D = ParticleArray  # noqa: F821  # pylint: disable=undefined-variable
ParticleArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member


behavior.update(awkward._util.copy_behaviors("PolarTwoVector", "MissingET", behavior))  # pylint: disable=protected-access


@awkward.mixin_class(behavior)
class MissingET(vector.PolarTwoVector, base.NanoCollection, base.Systematic):
    """Missing transverse energy collection."""

    @property
    def r(self):
        """Distance from origin in XY plane"""
        return self["met"]

    def _build_variations(self, _name, what, varying_function):
        """Build MET variations."""
        return varying_function(self, what)

    def describe_variations(self):
        """Return list of MET variation names."""
        return []

    def explodes_how(self):
        """MET variations are independent."""
        return "independent"


_set_repr_name("MissingET")

MissingETArray.ProjectionClass2D = MissingETArray  # noqa: F821  # pylint: disable=undefined-variable
MissingETArray.ProjectionClass3D = vector.SphericalThreeVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
MissingETArray.ProjectionClass4D = vector.LorentzVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
MissingETArray.MomentumClass = MissingETArray  # noqa: F821  # pylint: disable=undefined-variable

behavior.update(awkward._util.copy_behaviors("Particle", "Photon", behavior))  # pylint: disable=protected-access


@awkward.mixin_class(behavior)
class Photon(Particle, base.NanoCollection, base.Systematic):
    """Photon particle collection."""

    @property
    def mass(self):
        """Return zero mass for photon."""
        return awkward.zeros_like(self.pt)

    @property
    def charge(self):
        """Return zero charge for photon."""
        return awkward.zeros_like(self.pt)

    @property
    def isEM(self):
        return self.isEM_syst.NOSYS == 0  # pylint: disable=no-member

    def pass_isEM(self, words: list[PhotonID]):
        # 0 is pass, 1 is fail
        return (
            self.isEM_syst.NOSYS & reduce(ior, (1 << word.value for word in words))  # pylint: disable=no-member
        ) == 0

    def _build_variations(self, _name, what, varying_function):
        """Build photon variations."""
        return varying_function(self, what)

    def describe_variations(self):
        """Return list of photon variation names."""
        return []

    def explodes_how(self):
        """Photon variations are independent."""
        return "independent"


_set_repr_name("Photon")

PhotonArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
PhotonArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
PhotonArray.ProjectionClass4D = PhotonArray  # noqa: F821  # pylint: disable=undefined-variable
PhotonArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member

behavior.update(awkward._util.copy_behaviors("Particle", "Electron", behavior))  # pylint: disable=protected-access


@awkward.mixin_class(behavior)
class Electron(Particle, base.NanoCollection, base.Systematic):
    """Electron particle collection."""

    @property
    def mass(self):
        """Electron mass in MeV"""
        return awkward.ones_like(self.pt) * particle.literals.e_minus.mass  # pylint: disable=no-member

    def _build_variations(self, _name, what, varying_function):
        """Build electron variations."""
        return varying_function(self, what)

    def describe_variations(self):
        """Return list of electron variation names."""
        return []

    def explodes_how(self):
        """Electron variations are independent."""
        return "independent"


_set_repr_name("Electron")

ElectronArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
ElectronArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
ElectronArray.ProjectionClass4D = ElectronArray  # noqa: F821  # pylint: disable=undefined-variable
ElectronArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member

behavior.update(awkward._util.copy_behaviors("Particle", "Muon", behavior))  # pylint: disable=protected-access


@awkward.mixin_class(behavior)
class Muon(Particle, base.NanoCollection, base.Systematic):
    """Muon particle collection."""

    @property
    def mass(self):
        """Muon mass in MeV"""
        return awkward.ones_like(self.pt) * particle.literals.mu_minus.mass  # pylint: disable=no-member

    def _build_variations(self, _name, what, varying_function):
        """Build muon variations."""
        return varying_function(self, what)

    def describe_variations(self):
        """Return list of muon variation names."""
        return []

    def explodes_how(self):
        """Muon variations are independent."""
        return "independent"


_set_repr_name("Muon")

MuonArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
MuonArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
MuonArray.ProjectionClass4D = MuonArray  # noqa: F821  # pylint: disable=undefined-variable
MuonArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member

behavior.update(awkward._util.copy_behaviors("Particle", "Tau", behavior))  # pylint: disable=protected-access


@awkward.mixin_class(behavior)
class Tau(Particle, base.NanoCollection, base.Systematic):
    """Tau particle collection."""

    @property
    def mass(self):
        """Tau mass in MeV"""
        return awkward.ones_like(self.pt) * particle.literals.tau_minus.mass  # pylint: disable=no-member

    def _build_variations(self, _name, what, varying_function):
        """Build tau variations."""
        return varying_function(self, what)

    def describe_variations(self):
        """Return list of tau variation names."""
        return []

    def explodes_how(self):
        """Tau variations are independent."""
        return "independent"


_set_repr_name("Tau")

TauArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
TauArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
TauArray.ProjectionClass4D = TauArray  # noqa: F821  # pylint: disable=undefined-variable
TauArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member


behavior.update(awkward._util.copy_behaviors("Particle", "Jet", behavior))  # pylint: disable=protected-access


@awkward.mixin_class(behavior)
class Jet(Particle, base.NanoCollection, base.Systematic):
    """Jet particle collection."""

    @property
    def mass(self):
        r"""Invariant mass (+, -, -, -)

        :math:`\sqrt{t^2-x^2-y^2-z^2}`
        """
        return self["m"]

    def _build_variations(self, _name, what, varying_function):
        """Build jet variations."""
        return varying_function(self, what)

    def describe_variations(self):
        """Return list of jet variation names."""
        return []

    def explodes_how(self):
        """Jet variations are independent."""
        return "independent"


_set_repr_name("Jet")

JetArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
JetArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member
JetArray.ProjectionClass4D = JetArray  # noqa: F821  # pylint: disable=undefined-variable
JetArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821  # pylint: disable=undefined-variable,no-member

__all__ = [
    "Electron",
    "ElectronArray",  # noqa: F822  # pylint: disable=undefined-all-variable
    "ElectronRecord",  # noqa: F822  # pylint: disable=undefined-all-variable
    "Jet",
    "JetArray",  # noqa: F822  # pylint: disable=undefined-all-variable
    "JetRecord",  # noqa: F822  # pylint: disable=undefined-all-variable
    "MissingET",
    "MissingETArray",  # noqa: F822  # pylint: disable=undefined-all-variable
    "MissingETRecord",  # noqa: F822  # pylint: disable=undefined-all-variable
    "Muon",
    "MuonArray",  # noqa: F822  # pylint: disable=undefined-all-variable
    "MuonRecord",  # noqa: F822  # pylint: disable=undefined-all-variable
    "NtupleEvents",
    "Particle",
    "ParticleArray",  # noqa: F822  # pylint: disable=undefined-all-variable
    "ParticleRecord",  # noqa: F822  # pylint: disable=undefined-all-variable
    "Pass",
    "Photon",
    "PhotonArray",  # noqa: F822  # pylint: disable=undefined-all-variable
    "PhotonRecord",  # noqa: F822  # pylint: disable=undefined-all-variable
    "Weight",
]
