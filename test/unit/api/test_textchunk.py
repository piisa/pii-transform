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
    Patch the API used by textchunk
    """
    # Patch the pii-extract-base API
    processor_mock = Mock()
    collection_mock = Mock(return_value=piic)
    monkeypatch.setattr(mod, "MISSING_MOD", None)
    monkeypatch.setattr(mod, "PiiProcessor", processor_mock)
    monkeypatch.setattr(mod, "PiiCollectionBuilder", collection_mock)
    monkeypatch.setattr(mod, "PII_EXTRACT_VERSION", "0.6.1")

    def decide(piic, chunk):
        return piic

    # Set the pii-decide PiiDecider to be a mock
    decider_mock = Mock()
    decider_mock.decide_chunk = decide
    decider_cls = Mock(return_value=decider_mock)
    monkeypatch.setattr(mod, "PiiDecider", decider_cls)


# -----------------------------------------------------------------------


def test10_constructor(monkeypatch):
    """
    Test constructing the object
    """
    patch_pii_extract(monkeypatch)

    m = mod.PiiTextProcessor(default_policy="annotate")
    assert str(m) == "<PiiTextProcessor [annotate]>"


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

    # Open sample text
    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()

    # Create a processor
    m = mod.PiiTextProcessor(default_policy="annotate")
    assert str(m) == "<PiiTextProcessor [annotate]>"

    # Process!
    got = m(src)

    # Open expected result
    with open(DATADIR / "example-trf.txt", encoding="utf-8") as f:
        exp = f.read()

    #print("EXP", exp, "GOT", got, sep="\n")
    assert exp == got
