# atlas-schema v0.2.4

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- SPHINX-START -->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/scipp-atlas/atlas-schema/workflows/CI/badge.svg
[actions-link]:             https://github.com/scipp-atlas/atlas-schema/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/atlas-schema
[conda-link]:               https://github.com/conda-forge/atlas-schema-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/scipp-atlas/atlas-schema/discussions
[pypi-link]:                https://pypi.org/project/atlas-schema/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/atlas-schema
[pypi-version]:             https://img.shields.io/pypi/v/atlas-schema
[rtd-badge]:                https://readthedocs.org/projects/atlas-schema/badge/?version=latest
[rtd-link]:                 https://atlas-schema.readthedocs.io/en/latest/?badge=latest

<!-- prettier-ignore-end -->

This is the python package containing schemas and helper functions enabling
analyzers to work with ATLAS datasets (Monte Carlo and Data), using
[coffea](https://coffea-hep.readthedocs.io/en/latest/).

## Hello World

The simplest example is to just get started processing the file as expected:

```python
from atlas_schema.schema import NtupleSchema
from coffea import dataset_tools
import awkward as ak

fileset = {"ttbar": {"files": {"path/to/ttbar.root": "tree_name"}}}
samples, report = dataset_tools.preprocess(fileset)


def noop(events):
    return ak.fields(events)


fields = dataset_tools.apply_to_fileset(noop, samples, schemaclass=NtupleSchema)
print(fields)
```

which produces something similar to

```python
{
    "ttbar": [
        "dataTakingYear",
        "mcChannelNumber",
        "runNumber",
        "eventNumber",
        "lumiBlock",
        "actualInteractionsPerCrossing",
        "averageInteractionsPerCrossing",
        "truthjet",
        "PileupWeight",
        "RandomRunNumber",
        "met",
        "recojet",
        "truth",
        "generatorWeight",
        "beamSpotWeight",
        "trigPassed",
        "jvt",
    ]
}
```

However, a more involved example to apply a selection and fill a histogram looks
like below:

```python
import awkward as ak
import dask
import hist.dask as had
import matplotlib.pyplot as plt
from coffea import processor
from coffea.nanoevents import NanoEventsFactory
from distributed import Client

from atlas_schema.schema import NtupleSchema


class MyFirstProcessor(processor.ProcessorABC):
    def __init__(self):
        pass

    def process(self, events):
        dataset = events.metadata["dataset"]
        h_ph_pt = (
            had.Hist.new.StrCat(["all", "pass", "fail"], name="isEM")
            .Regular(200, 0.0, 2000.0, name="pt", label="$pt_{\gamma}$ [GeV]")
            .Int64()
        )

        cut = ak.all(events.ph.isEM, axis=1)
        h_ph_pt.fill(isEM="all", pt=ak.firsts(events.ph.pt / 1.0e3))
        h_ph_pt.fill(isEM="pass", pt=ak.firsts(events[cut].ph.pt / 1.0e3))
        h_ph_pt.fill(isEM="fail", pt=ak.firsts(events[~cut].ph.pt / 1.0e3))

        return {
            dataset: {
                "entries": ak.num(events, axis=0),
                "ph_pt": h_ph_pt,
            }
        }

    def postprocess(self, accumulator):
        pass


if __name__ == "__main__":
    client = Client()

    fname = "ntuple.root"
    events = NanoEventsFactory.from_root(
        {fname: "analysis"},
        schemaclass=NtupleSchema,
        metadata={"dataset": "700352.Zqqgamma.mc20d.v1"},
    ).events()

    p = MyFirstProcessor()
    out = p.process(events)
    (computed,) = dask.compute(out)
    print(computed)

    fig, ax = plt.subplots()
    computed["700352.Zqqgamma.mc20d.v1"]["ph_pt"].plot1d(ax=ax)
    ax.set_xscale("log")
    ax.legend(title="Photon pT for Zqqgamma")

    fig.savefig("ph_pt.pdf")
```

which produces

<img src="https://raw.githubusercontent.com/scipp-atlas/atlas-schema/main/docs/_static/img/ph_pt.png" alt="three stacked histograms of photon pT, with each stack corresponding to: no selection, requiring the isEM flag, and inverting the isEM requirement" width="500" style="display: block; margin-left: auto; margin-right: auto;">

<!-- SPHINX-END -->

## Developer Notes

### Converting Enums from C++ to Python

This useful `vim` substitution helps:

```
%s/    \([A-Za-z]\+\)\s\+=  \(\d\+\),\?/    \1: Annotated[int, "\1"] = \2
```
