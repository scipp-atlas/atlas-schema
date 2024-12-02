"""Mixins for the Ntuple schema"""

from __future__ import annotations

from functools import reduce
from operator import ior

import awkward
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
        return f"<event {getattr(self,'runNumber','??')}:\
                {getattr(self,'eventNumber','??')}:\
                {getattr(self,'mcChannelNumber','??')}>"


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


@awkward.mixin_class(behavior)
class MasslessParticle(Particle, base.NanoCollection):
    @property
    def mass(self):
        r"""Invariant mass (+, -, -, -)

        :math:`\sqrt{t^2-x^2-y^2-z^2}`
        """
        return 0.0 * self.pt


_set_repr_name("MasslessParticle")


@awkward.mixin_class(behavior)
class MissingET(MasslessParticle, base.NanoCollection, base.Systematic):
    @property
    def pt(self):
        """Alias for `r`"""
        return self["met"] / 1.0e3

    @property
    def eta(self):
        r"""Pseudorapidity

        :math:`-\ln\tan(\theta/2) = \text{arcsinh}(z/r)`
        """
        return 0.0 * self.pt


_set_repr_name("MissingET")


@awkward.mixin_class(behavior)
class Photon(MasslessParticle, base.NanoCollection, base.Systematic):
    @property
    def isEM(self):
        return self.isEM_syst.NOSYS == 0

    def pass_isEM(self, words: list[PhotonID]):
        # 0 is pass, 1 is fail
        return (
            self.isEM_syst.NOSYS & reduce(ior, (1 << word.value for word in words))
        ) == 0


_set_repr_name("Photon")


@awkward.mixin_class(behavior)
class Electron(MasslessParticle, base.NanoCollection, base.Systematic): ...


_set_repr_name("Electron")


@awkward.mixin_class(behavior)
class Muon(MasslessParticle, base.NanoCollection, base.Systematic): ...


_set_repr_name("Muon")


@awkward.mixin_class(behavior)
class Jet(Particle, base.NanoCollection, base.Systematic): ...


_set_repr_name("Jet")


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
