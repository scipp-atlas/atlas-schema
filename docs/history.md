# Changelog

All notable changes to atlas-schema will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

**_Changed:_**

**_Added:_**

**_Fixed:_**

(atlas-schema-v0.3.0)=

## [0.3.0](https://github.com/scipp-atlas/atlas-schema/releases/tag/v0.3.0) - 2025-07-29

**_Changed:_**

- `dask_awkward` code has been dropped {pr}`65`
- updated `README` and examples to use the new `coffea.processor` interface
- `coffea` dependency bumped up to `2025.7.x+`

(atlas-schema-v0.2.5)=

## [0.2.5](https://github.com/scipp-atlas/atlas-schema/releases/tag/v0.2.5) - 2025-03-31

**_Added:_**

- `RuntimeWarning` when parsing a branch that does not match the structure
  defined by the schema

**_Fixed:_**

- Improved handling of `singletons` {pr}`52` so we don't try to parse the branch
  for the collection

(atlas-schema-v0.2.4)=

## [0.2.4](https://github.com/scipp-atlas/atlas-schema/releases/tag/v0.2.4) - 2025-02-19

**_Changed:_**

- Significant amount of documentation for how
  {class}`atlas_schema.schema.NtupleSchema` works

**_Added:_**

- New `autosummary` templates to render improved/cleaner documentation pages

**_Fixed:_**

- Custom collections with underscores are now properly handled ({pr}`50`)
- Behaviors were being checked for singletons when they should not have been
  ({pr}`51`)

(atlas-schema-v0.2.3)=

## [0.2.3](https://github.com/scipp-atlas/atlas-schema/releases/tag/v0.2.3) - 2025-02-15

**_Changed:_**

**_Fixed:_**

- Singleton branches were not handled properly in some ntuples used by `ATLAS`
  analyzers. Now, the schema will raise a {class}`RuntimeWarning` if the user
  does not explicitly define the singletons they have in their input files. See
  additionally the {ref}`faq` for some details as well. ({issue}`19`, {pr}`48`)

(atlas-schema-v0.2.2)=

## [0.2.2](https://github.com/scipp-atlas/atlas-schema/releases/tag/v0.2.2) - 2025-02-13

**_Changed:_**

- additional functionality to support multiple `__getitem__` for the
  {mod}`atlas_schema.enums` classes ({pr}`44`) which now supports an API as
  follows:
  ```python
  ats.enums.ParticleOrigin["NonDefined"]
  ats.enums.ParticleOrigin["NonDefined", "BremPhoton"]
  ```

**_Added:_**

- {func}`atlas_schema.isin` for a naive implementation of `x in values` as
  `isin(x, values)`, ({issue}`42`, {pr}`43`)

(atlas-schema-v0.2.1)=

## [0.2.1](https://github.com/scipp-atlas/atlas-schema/releases/tag/v0.2.1) - 2025-02-06

**_Changed:_**

- migrated `MissingET` to `PolarTwoVector` ({issue}`35`, {pr}`36`)
- mixin support for {pypi}`vector` classes ({issue}`34`, {pr}`36`)

**_Added:_**

- this documentation ({pr}`37`)

(atlas-schema-v0.2.0)=

## [0.2.0](https://github.com/scipp-atlas/atlas-schema/releases/tag/v0.2.0) - 2024-11-19

**_Changed:_**

- drop python 3.8

(atlas-schema-v0.1.0)=

## [0.1.0](https://github.com/scipp-atlas/atlas-schema/releases/tag/v0.1.0) - 2024-11-18

**_Added:_**

- first release of this package!
