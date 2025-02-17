from __future__ import annotations

import warnings
from collections.abc import KeysView, ValuesView
from typing import Any, ClassVar

from coffea.nanoevents.schemas.base import BaseSchema, zip_forms

from atlas_schema.typing_compat import Behavior, Self


class NtupleSchema(BaseSchema):  # type: ignore[misc]
    """Ntuple schema builder

    The Ntuple schema is built from all branches found in the supplied file, based on
    the naming pattern of the branches. This naming pattern is assumed to be

    .. code-block:: bash

       {collection:str}_{subcollection:str}_{systematic:str}

    where:
      * ``collection`` is assumed to be a prefix with typical characters, following the regex ``[a-zA-Z][a-zA-Z0-9]*``; that is starting with a case-insensitive letter, and proceeded by zero or more alphanumeric characters,
      * ``subcollection`` is assumed to be anything with typical characters (allowing for underscores) following the regex ``[a-zA-Z_][a-zA-Z0-9_]*``; that is starting with a case-insensitive letter or underscore, and proceeded by zero or more alphanumeric characters including underscores, and
      * ``systematic`` is assumed to be either ``NOSYS`` to indicate a branch with potential systematic variariations, or anything with typical characters (allowing for underscores) following the same regular expression as the ``subcollection``.

    Here, a collection refers to the top-level entry to access an item - a collection called ``el`` will be accessible under the ``el`` attributes via ``events['el']`` or ``events.el``. A subcollection called ``pt`` will be accessible under that collection, such as ``events['el']['pt']`` or ``events.el.pt``. This is the power of the schema providing a more user-friendly (and programmatic) access to the underlying branches.

    The above logic means that the following branches below will be categorized as ``(collection, subcollection, systematic)`` tuples:
      * ``actualInteractionsPerCrossing``: ``('actualInteractionsPerCrossing', None, None)``
      * ``eventNumber``: ``('eventNumber', None, None)``
      * ``runNumber``: ``('runNumber', None, None)``
      * ``el_pt_NOSYS``: ``('el', 'pt', 'NOSYS')``
      * ``jet_cleanTightBad_NOSYS``: ``('jet', 'cleanTightBad', 'NOSYS')``
      * ``jet_select_btag_NOSYS``: ``('jet', 'select_btag', 'NOSYS')``
      * ``jet_e_NOSYS``: ``('jet', 'e', 'NOSYS')``
      * ``truthel_phi``: ``('truthel', 'phi', None)``
      * ``truthel_pt``: ``('truthel', 'pt', None)``
      * ``ph_eta``: ``('ph', 'eta', None)``
      * ``ph_phi``: ``('ph', 'phi', None)``
      * ``mu_TTVA_effSF_baseline_NOSYS``: ``('mu', 'TTVA_effSF_baseline', 'NOSYS')``
      * ``recojet_antikt4PFlow_passesOR_MUON_SAGITTA_RESBIAS__1up``: ``('recojet', 'antikt4PFlow_passesOR', 'MUON_SAGITTA_RESBIAS__1up')``
      * ``recojet_antikt4PFlow_passesOR_NOSYS``: ``('recojet', 'antikt4PFlow_passesOR', 'NOSYS')``
      * ``recojet_antikt10UFO_m``: ``('recojet', 'antikt10UFO_m', None)``

    Sometimes this logic is not what you want, and there are ways to teach ``NtupleSchema`` how to group some of these better for atypical cases. We can address these case-by-case.

    ## Singletons

    Sometimes you have particular branches that you don't want to be treated as a collection (with subcollections). And sometimes you will see warnings about this (see :ref:`faq`). There are some pre-defined ``singletons`` stored under :attr:`event_ids`, and these will be lazily treated as a _singleton_. For other cases where you add your own branches, you can additionally extend this class to add your own ``singletons``:

    .. code-block:: python

       from atlas_schema.schema import NtupleSchema


       class MySchema(NtupleSchema):
           singletons = {"RandomRunNumber"}

    and use this schema in your analysis code. The rest of the logic will be handled for you, and you can access your singletons under ``events.RandomRunNumber`` as expected.

    ## Mixins (collections, subcollections)

    In more complicated scenarios, you might need to teach :class:`NtupleSchema` how to handle collections that end up having underscores in their name, or other characters that make the grouping non-trivial. In some other scenarios, you want to tell the schema to assign a certain set of behaviors to a collection - rather than the default :class:`atlas_schema.methods.Particle` behavior. This is where ``mixins`` comes in. Similar to how ``singletons`` are handled, you extend this schema to include your own mixins pointing them at one of the behaviors defined in :module:`atlas_schema.methods`.

    Let's demonstrate both cases. Imagine you want to have your ``truthel`` collections above treated as :class:`atlas_schema.methods.Electron`, then you would extend the existing ``mixins``:

    .. code-block:: python

       from atlas_schema.schema import NtupleSchema


       class MySchema(NtupleSchema):
           mixins = {"truthel": "Electron", **NtupleSchema.mixins}

    Now, ``events.truthel`` will give you arrays zipped up with :class:`atlas_schema.methods.Electron` behaviors.

    If instead, you run into problems with mixing different branches in the same collection, because the default behavior of this schema described above is not smart enough to handle the atypical cases, you can explicitly fix this by defining your collections:

    .. code-block:: python

       from atlas_schema.schema import NtupleSchema


       class MySchema(NtupleSchema):
           mixins = {
               "recojet_antikt4PFlow": "Jet",
               "recojet_antikt10UFO": "Jet",
               **NtupleSchema.mixins,
           }

    Now, ``events.recojet_antikt4PFlow`` and ``events.recojet_antikt10UFO`` will be separate collections, instead of a single ``events.recojet`` that incorrectly merged branches from each of these collections.
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
    singletons: ClassVar[set[str]] = set()

    docstrings: ClassVar[dict[str, str]] = {
        "charge": "charge",
        "eta": "pseudorapidity",
        "met": "missing transverse energy [MeV]",
        "mass": "invariant mass [MeV]",
        "pt": "transverse momentum [MeV]",
        "phi": "azimuthal angle",
    }

    def __init__(self, base_form: dict[str, Any], version: str = "latest"):
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
    def v1(cls, base_form: dict[str, Any]) -> Self:
        """Build the NtupleEvents

        For example, one can use ``NanoEventsFactory.from_root("file.root", schemaclass=NtupleSchema.v1)``
        to ensure NanoAODv7 compatibility.
        """
        return cls(base_form, version="1")

    def _build_collections(
        self, field_names: list[str], input_contents: list[Any]
    ) -> tuple[KeysView[str], ValuesView[dict[str, Any]]]:
        branch_forms = dict(zip(field_names, input_contents))

        # parse into high-level records (collections, list collections, and singletons)
        collections = {k.split("_")[0] for k in branch_forms}
        collections -= self.event_ids
        collections -= set(self.singletons)

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

        # first, register singletons (event-level, others)
        for name in {*self.event_ids, *self.singletons}:
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

            if not used and not content:
                warnings.warn(
                    f"I identified a branch that likely does not have any leaves: '{name}'. I will treat this as a 'singleton'. To suppress this warning next time, please define your singletons explicitly.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                self.singletons.add(name)
                output[name] = branch_forms[name]

            else:
                output[name] = zip_forms(content, name, record_name=mixin)

            output[name].setdefault("parameters", {})
            output[name]["parameters"].update({"collection_name": name})

            if output[name]["class"] == "ListOffsetArray":
                parameters = output[name]["content"]["fields"]
                contents = output[name]["content"]["contents"]
            elif output[name]["class"] == "RecordArray":
                parameters = output[name]["fields"]
                contents = output[name]["contents"]
            elif output[name]["class"] == "NumpyArray":
                # these are singletons that we just pass through
                continue
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

        return output.keys(), output.values()

    @classmethod
    def behavior(cls) -> Behavior:
        """Behaviors necessary to implement this schema"""
        from atlas_schema.methods import behavior as roaster

        return roaster
