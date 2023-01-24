"""
Test the PiiTextProcessor class
"""

from pathlib import Path

from pii_data.types.piicollection.loader import PiiCollectionLoader

import pii_transform.api.e2e.textchunk as mod

from unittest.mock import Mock


DATADIR = Path(__file__).parents[2] / "data" / "chunk"


def patch_pii_extract(monkeypatch, piic=None):
    """
    Patch the pii-extract-base API used by textchunk
    """
    processor_mock = Mock()
    collection_mock = Mock(return_value=piic)
    monkeypatch.setattr(mod, "MISSING", None)
    monkeypatch.setattr(mod, "PiiProcessor", processor_mock)
    monkeypatch.setattr(mod, "PiiCollectionBuilder", collection_mock)


# -----------------------------------------------------------------------


def test10_constructor(monkeypatch):
    """
    Test constructing the object
    """
    patch_pii_extract(monkeypatch)

    m = mod.PiiTextProcessor()
    assert str(m) == "<PiiTextProcessor [label]>"


def test20_process_chunk(monkeypatch):
    """
    Test processing a text buffer
    """
    piic = PiiCollectionLoader()
    piic.load_json(DATADIR / "example-pii.json")
    patch_pii_extract(monkeypatch, piic)

    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()

    m = mod.PiiTextProcessor(default_policy="annotate")
    assert str(m) == "<PiiTextProcessor [annotate]>"

    got = m(src)

    with open(DATADIR / "example-trf.txt", encoding="utf-8") as f:
        exp = f.read()

    assert exp == got


def test30_process_chunk_rev(monkeypatch):
    """
    Test processing a text buffer, unordered PII instances
    """
    piic = PiiCollectionLoader()
    piic.load_json(DATADIR / "example-pii-rev.json")
    patch_pii_extract(monkeypatch, piic)

    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()

    m = mod.PiiTextProcessor(default_policy="annotate")
    assert str(m) == "<PiiTextProcessor [annotate]>"

    got = m(src)

    with open(DATADIR / "example-trf.txt", encoding="utf-8") as f:
        exp = f.read()

    assert exp == got
