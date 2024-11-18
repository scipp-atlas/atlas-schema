# atlas-schema v0.1.0

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

## Developer Notes

### Converting Enums from C++ to Python

This useful `vim` substitution helps:

```
%s/    \([A-Za-z]\+\)\s\+=  \(\d\+\),\?/    \1: Annotated[int, "\1"] = \2
```
