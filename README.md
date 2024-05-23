# atlas v0.0.1

[![Actions Status][actions-badge]][actions-link]
[![Documentation Status][rtd-badge]][rtd-link]

[![PyPI version][pypi-version]][pypi-link]
[![Conda-Forge][conda-badge]][conda-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

[![GitHub Discussion][github-discussions-badge]][github-discussions-link]

<!-- SPHINX-START -->

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/scipp-atlas/atlas/workflows/CI/badge.svg
[actions-link]:             https://github.com/scipp-atlas/atlas/actions
[conda-badge]:              https://img.shields.io/conda/vn/conda-forge/atlas
[conda-link]:               https://github.com/conda-forge/atlas-feedstock
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/scipp-atlas/atlas/discussions
[pypi-link]:                https://pypi.org/project/atlas/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/atlas
[pypi-version]:             https://img.shields.io/pypi/v/atlas
[rtd-badge]:                https://readthedocs.org/projects/atlas/badge/?version=latest
[rtd-link]:                 https://atlas.readthedocs.io/en/latest/?badge=latest

<!-- prettier-ignore-end -->

## Developer Notes

### Converting Enums from C++ to Python

This useful `vim` substitution helps:

```
%s/    \([A-Za-z]\+\)\s\+=  \(\d\+\),\?/    \1: Annotated[int, "\1"] = \2
```
