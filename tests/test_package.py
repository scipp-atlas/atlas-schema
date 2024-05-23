from __future__ import annotations

import importlib.metadata

import atlas as m


def test_version():
    assert importlib.metadata.version("atlas") == m.__version__
