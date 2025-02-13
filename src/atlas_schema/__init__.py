"""
Copyright (c) 2024 Giordon Stark. All rights reserved.

atlas_schema: Collection of utilities and helper functions for HEP ATLAS analysers
"""

from __future__ import annotations

import warnings

from atlas_schema._version import version as __version__
from atlas_schema.enums import ParticleOrigin, PhotonID
from atlas_schema.utils import isin

warnings.filterwarnings("ignore", module="coffea.*")

__all__ = ["ParticleOrigin", "PhotonID", "__version__", "isin"]
