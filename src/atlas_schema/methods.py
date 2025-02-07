"""Mixins for the Ntuple schema"""

from __future__ import annotations

from functools import reduce
from operator import ior

import awkward
import particle
from coffea.nanoevents.methods import base, candidate, vector
from dask_awkward import dask_method

from atlas_schema.enums import PhotonID
from atlas_schema.typing_compat import Behavior

behavior: Behavior = {}
behavior.update(base.behavior)
# vector behavior is included in candidate behavior
behavior.update(candidate.behavior)


class NtupleEvents(behavior["NanoEvents"]):  # type: ignore[misc, valid-type, name-defined]
    def __repr__(self):
        return f"<event {getattr(self, 'runNumber', '??')}:\
                {getattr(self, 'eventNumber', '??')}:\
                {getattr(self, 'mcChannelNumber', '??')}>"


behavior["NanoEvents"] = NtupleEvents


def _set_repr_name(classname):
    def namefcn(_self):
        return classname

    behavior[("__typestr__", classname)] = classname[0].lower() + classname[1:]
    behavior[classname].__repr__ = namefcn


@awkward.mixin_class(behavior)
class Weight(base.NanoCollection, base.Systematic): ...


_set_repr_name("Weight")


@awkward.mixin_class(behavior)
class Pass(base.NanoCollection, base.Systematic): ...


_set_repr_name("Pass")

behavior.update(
    awkward._util.copy_behaviors("PtEtaPhiMLorentzVector", "Particle", behavior)
)


@awkward.mixin_class(behavior)
class Particle(vector.PtEtaPhiMLorentzVector):
    """Generic particle collection that has Lorentz vector properties

    Also handles the following additional branches:
    - '{obj}_select'
    """

    @property
    def mass(self):
        r"""Invariant mass (+, -, -, -)

        :math:`\sqrt{t^2-x^2-y^2-z^2}`
        """
        return self["mass"] / 1.0e3

    @dask_method
    def passes(self, name):
        return self[f"select_{name}"] == 1

    @passes.dask
    def passes(self, dask_array, name):
        return dask_array[f"select_{name}"] == 1

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

ParticleArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821
ParticleArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821
ParticleArray.ProjectionClass4D = ParticleArray  # noqa: F821
ParticleArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821


behavior.update(awkward._util.copy_behaviors("PolarTwoVector", "MissingET", behavior))


@awkward.mixin_class(behavior)
class MissingET(vector.PolarTwoVector, base.NanoCollection, base.Systematic):
    @property
    def r(self):
        """Distance from origin in XY plane"""
        return self["met"]


_set_repr_name("MissingET")

MissingETArray.ProjectionClass2D = MissingETArray  # noqa: F821
MissingETArray.ProjectionClass3D = vector.SphericalThreeVectorArray  # noqa: F821
MissingETArray.ProjectionClass4D = vector.LorentzVectorArray  # noqa: F821
MissingETArray.MomentumClass = MissingETArray  # noqa: F821

behavior.update(awkward._util.copy_behaviors("Particle", "Photon", behavior))


@awkward.mixin_class(behavior)
class Photon(Particle, base.NanoCollection, base.Systematic):
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
        return self.isEM_syst.NOSYS == 0

    def pass_isEM(self, words: list[PhotonID]):
        # 0 is pass, 1 is fail
        return (
            self.isEM_syst.NOSYS & reduce(ior, (1 << word.value for word in words))
        ) == 0


_set_repr_name("Photon")

PhotonArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821
PhotonArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821
PhotonArray.ProjectionClass4D = PhotonArray  # noqa: F821
PhotonArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821

behavior.update(awkward._util.copy_behaviors("Particle", "Electron", behavior))


@awkward.mixin_class(behavior)
class Electron(Particle, base.NanoCollection, base.Systematic):
    @property
    def mass(self):
        """Electron mass in GeV"""
        return particle.literals.e_minus.mass / 1.0e3


_set_repr_name("Electron")

ElectronArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821
ElectronArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821
ElectronArray.ProjectionClass4D = ElectronArray  # noqa: F821
ElectronArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821

behavior.update(awkward._util.copy_behaviors("Particle", "Muon", behavior))


@awkward.mixin_class(behavior)
class Muon(Particle, base.NanoCollection, base.Systematic):
    @property
    def mass(self):
        """Muon mass in GeV"""
        return particle.literals.mu_minus.mass / 1.0e3


_set_repr_name("Muon")

MuonArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821
MuonArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821
MuonArray.ProjectionClass4D = MuonArray  # noqa: F821
MuonArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821

behavior.update(awkward._util.copy_behaviors("Particle", "Tau", behavior))


@awkward.mixin_class(behavior)
class Tau(Particle, base.NanoCollection, base.Systematic):
    @property
    def mass(self):
        """Tau mass in GeV"""
        return particle.literals.tau_minus.mass / 1.0e3


_set_repr_name("Tau")

TauArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821
TauArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821
TauArray.ProjectionClass4D = TauArray  # noqa: F821
TauArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821


behavior.update(awkward._util.copy_behaviors("Particle", "Jet", behavior))


@awkward.mixin_class(behavior)
class Jet(Particle, base.NanoCollection, base.Systematic): ...


_set_repr_name("Jet")

JetArray.ProjectionClass2D = vector.TwoVectorArray  # noqa: F821
JetArray.ProjectionClass3D = vector.ThreeVectorArray  # noqa: F821
JetArray.ProjectionClass4D = JetArray  # noqa: F821
JetArray.MomentumClass = vector.LorentzVectorArray  # noqa: F821

__all__ = [
    "Electron",
    "Jet",
    "MissingET",
    "Muon",
    "NtupleEvents",
    "Particle",
    "Pass",
    "Photon",
    "Weight",
]
