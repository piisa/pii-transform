"""
Test the MultiPiiTextProcessor class
"""

from pathlib import Path

from pii_data.types.doc import DocumentChunk
from pii_data.types.piicollection.loader import PiiCollectionLoader
from pii_data.helper.exception import ProcException

import pii_transform.api.e2e.multilang as mod

from unittest.mock import Mock
import pytest

DATADIR = Path(__file__).parents[2] / "data" / "chunk"


def patch_pii_extract(monkeypatch, piic=None):
    """
    Patch the pii-extract-base API used by textchunk
    """
    processor_mock = Mock()
    processor_cls = Mock(return_value=processor_mock)
    collection_mock = Mock(return_value=piic)
    # Remove the mark of import fail
    monkeypatch.setattr(mod, "MISSING", None)
    # Set the processor to be a mock
    monkeypatch.setattr(mod, "PII_EXTRACT_VERSION", "0.3.0")
    monkeypatch.setattr(mod, "PiiProcessor", processor_cls)
    monkeypatch.setattr(mod, "PiiCollectionBuilder", collection_mock)
    return processor_mock


# -----------------------------------------------------------------------


def test10_constructor(monkeypatch):
    """
    Test constructing the object
    """
    mock = patch_pii_extract(monkeypatch)

    m = mod.MultiPiiTextProcessor(["en", "es"])
    assert str(m) == "<MultiPiiTextProcessor [#2 label]>"

    assert mock.build_tasks.call_count == 2



def test11_constructor_error(monkeypatch):
    """
    Test constructing the object, error
    """
    patch_pii_extract(monkeypatch)

    with pytest.raises(TypeError):
        mod.MultiPiiTextProcessor()


def test20_process_chunk(monkeypatch):
    """
    Test processing a text buffer
    """
    piic = PiiCollectionLoader()
    piic.load_json(DATADIR / "example-pii.json")
    patch_pii_extract(monkeypatch, piic)

    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()

    m = mod.MultiPiiTextProcessor(["en", "es"], default_policy="annotate")
    assert str(m) == "<MultiPiiTextProcessor [#2 annotate]>"

    with open(DATADIR / "example-trf.txt", encoding="utf-8") as f:
        exp = f.read()

    got = m(src, "en")
    assert exp == got

    # We get the same result, since we are patching detection
    got = m(src, "es")
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

    m = mod.MultiPiiTextProcessor(["en"], default_policy="annotate")
    assert str(m) == "<MultiPiiTextProcessor [#1 annotate]>"

    with open(DATADIR / "example-trf.txt", encoding="utf-8") as f:
        exp = f.read()

    got = m(src, "en")
    assert exp == got


def test50_process_chunk_err(monkeypatch):
    """
    Test processing a text buffer, error
    """
    piic = PiiCollectionLoader()
    piic.load_json(DATADIR / "example-pii.json")
    patch_pii_extract(monkeypatch, piic)

    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()

    m = mod.MultiPiiTextProcessor(["en", "es"], default_policy="annotate")

    # A chunk with no language
    chunk = DocumentChunk(id=0, data=src)
    with pytest.raises(ProcException):
        m.process(chunk)
