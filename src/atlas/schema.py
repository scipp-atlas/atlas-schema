from __future__ import annotations

import warnings
from collections.abc import KeysView, ValuesView
from typing import Any, ClassVar

from coffea.nanoevents.schemas.base import BaseSchema, zip_forms


class NtupleSchema(BaseSchema):  # type: ignore[misc]
    """Ntuple schema builder

    The Ntuple schema is built from all branches found in the supplied file, based on
    the naming pattern of the branches. The following additional arrays are constructed:

    - n/a
    """

    __dask_capable__ = True

    warn_missing_crossrefs = True
    error_missing_event_ids = False

    event_ids_data: ClassVar[set[str]] = {
        "lumiBlock",
        "averageInteractionsPerCrossing",
        "actualInteractionsPerCrossing",
        "dataTakingYear",
    }
    event_ids_mc: ClassVar[set[str]] = {
        "mcChannelNumber",
        "runNumber",
        "eventNumber",
        "mcEventWeights",
    }
    event_ids: ClassVar[set[str]] = {*event_ids_data, *event_ids_mc}

    mixins: ClassVar[dict[str, str]] = {
        "el": "Electron",
        "jet": "Jet",
        "met": "MissingET",
        "mu": "Muon",
        "pass": "Pass",
        "ph": "Photon",
        "trigPassed": "Trigger",
        "weight": "Weight",
    }

    # These are stored as length-1 vectors unnecessarily
    singletons: ClassVar[list[str]] = []

    docstrings: ClassVar[dict[str, str]] = {
        "charge": "charge",
        "eta": "pseudorapidity",
        "met": "missing transverse energy [MeV]",
        "mass": "invariant mass [MeV]",
        "pt": "transverse momentum [MeV]",
        "phi": "azimuthal angle",
    }

    def __init__(self, base_form, version="latest"):
        super().__init__(base_form)
        self._version = version
        if version == "latest":
            pass
        else:
            pass
        self._form["fields"], self._form["contents"] = self._build_collections(
            self._form["fields"], self._form["contents"]
        )
        self._form["parameters"]["metadata"]["version"] = self._version

    @classmethod
    def v1(cls, base_form):
        """Build the NtupleEvents

        For example, one can use ``NanoEventsFactory.from_root("file.root", schemaclass=NtupleSchema.v1)``
        to ensure NanoAODv7 compatibility.
        """
        return cls(base_form, version="1")

    def _build_collections(
        self, field_names, input_contents
    ) -> tuple[KeysView[str], ValuesView[dict[str, Any]]]:
        branch_forms = dict(zip(field_names, input_contents))
        # parse into high-level records (collections, list collections, and singletons)
        collections = {k.split("_")[0] for k in branch_forms}
        collections -= self.event_ids

        # rename needed because easyjet breaks the AMG assumptions
        # https://gitlab.cern.ch/easyjet/easyjet/-/issues/246
        for k in list(branch_forms):
            if "NOSYS" not in k:
                continue
            branch_forms[k.replace("_NOSYS", "") + "_NOSYS"] = branch_forms.pop(k)

        # these are collections with systematic variations
        subcollections = {
            k.split("__")[0].split("_", 1)[1].replace("_NOSYS", "")
            for k in branch_forms
            if "NOSYS" in k
        }

        # Check the presence of the event_ids
        missing_event_ids = [
            event_id for event_id in self.event_ids if event_id not in branch_forms
        ]

        if len(missing_event_ids) > 0:
            if self.error_missing_event_ids:
                msg = f"There are missing event ID fields: {missing_event_ids} \n\n\
                    The event ID fields {self.event_ids} are necessary to perform sub-run identification \
                    (e.g. for corrections and sub-dividing data during different detector conditions),\
                    to cross-validate MC and Data (i.e. matching events for comparison), and to generate event displays. \
                    It's advised to never drop these branches from the dataformat.\n\n\
                    This error can be demoted to a warning by setting the class level variable error_missing_event_ids to False."
                raise RuntimeError(msg)
            warnings.warn(
                f"Missing event_ids : {missing_event_ids}",
                RuntimeWarning,
                stacklevel=2,
            )

        output = {}

        # first, register the event-level stuff directly
        for name in self.event_ids:
            if name in missing_event_ids:
                continue
            output[name] = branch_forms[name]

        # next, go through and start grouping up collections
        for name in collections:
            mixin = self.mixins.get(name, "NanoCollection")
            content = {}
            used = set()

            for subname in subcollections:
                prefix = f"{name}_{subname}_"
                used.update({k for k in branch_forms if k.startswith(prefix)})
                subcontent = {
                    k[len(prefix) :]: branch_forms[k]
                    for k in branch_forms
                    if k.startswith(prefix)
                }
                if subcontent:
                    # create the nominal version
                    content[subname] = branch_forms[f"{prefix}NOSYS"]
                    # create a collection of the systematic variations for the given variable
                    content[f"{subname}_syst"] = zip_forms(
                        subcontent, f"{name}_syst", record_name="NanoCollection"
                    )

            content.update(
                {
                    k[len(name) + 1 :]: branch_forms[k]
                    for k in branch_forms
                    if k.startswith(name + "_") and k not in used
                }
            )

            output[name] = zip_forms(content, name, record_name=mixin)

            output[name].setdefault("parameters", {})
            output[name]["parameters"].update({"collection_name": name})

            if output[name]["class"] == "ListOffsetArray":
                parameters = output[name]["content"]["fields"]
                contents = output[name]["content"]["contents"]
            elif output[name]["class"] == "RecordArray":
                parameters = output[name]["fields"]
                contents = output[name]["contents"]
            else:
                msg = f"Unhandled class {output[name]['class']}"
                raise RuntimeError(msg)
            # update docstrings as needed
            # NB: must be before flattening for easier logic
            for index, parameter in enumerate(parameters):
                if "parameters" not in contents[index]:
                    continue

                parsed_name = parameter.replace("_NOSYS", "")
                contents[index]["parameters"]["__doc__"] = self.docstrings.get(
                    parsed_name,
                    contents[index]["parameters"].get(
                        "__doc__", "no docstring available"
                    ),
                )

            if name in self.singletons:
                # flatten! this 'promotes' the content of an inner dimension
                # upwards, effectively hiding one nested dimension
                output[name] = output[name]["content"]

        return output.keys(), output.values()

    @classmethod
    def behavior(cls):
        """Behaviors necessary to implement this schema"""
        from atlas.methods import behavior as roaster

        return roaster
