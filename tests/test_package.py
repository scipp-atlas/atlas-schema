from __future__ import annotations

import importlib.metadata

import atlas_schema as m


def test_version():
    assert importlib.metadata.version("atlas-schema") == m.__version__
