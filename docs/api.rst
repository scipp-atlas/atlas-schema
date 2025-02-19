Python API
==========

Top-Level
---------

.. currentmodule:: atlas_schema

.. autosummary::
   :toctree: _generated/
   :nosignatures:

   schema.NtupleSchema
   methods

Enums
-----

All enums listed below will typically allow you to access multiple values at once:

   >>> import atlas_schema as ats
   >>> ats.enums.ParticleOrigin['NonDefined']
   <ParticleOrigin.NonDefined: 0>
   >>> ats.enums.ParticleOrigin['NonDefined', 'Higgs']
   [<ParticleOrigin.NonDefined: 0>, <ParticleOrigin.Higgs: 14>]

.. currentmodule:: atlas_schema.enums

.. autosummary::
   :toctree: _generated/
   :nosignatures:

   ParticleType
   ParticleOrigin
   PhotonID


Functions
---------

.. currentmodule:: atlas_schema

.. autosummary::
   :toctree: _generated/
   :nosignatures:

   isin
