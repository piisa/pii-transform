"""
Test the MultiPiiTextProcessor class
"""

from pathlib import Path

from pii_data.types.doc import DocumentChunk
from pii_data.types.piicollection.loader import PiiCollectionLoader
from pii_data.types.piicollection import PiiDetector
from pii_data.helper.exception import ProcException

import pii_extract.api.processor as processor

import pii_transform.api.e2e.multilang as mod

from unittest.mock import Mock
import pytest

DATADIR = Path(__file__).parents[2] / "data" / "chunk"


def patch_pii_extract(monkeypatch,
                      piic_result: processor.PiiCollectionBuilder = None):
    """
    Patch the pii-extract-base API used by textchunk
    """

    def detect(chunk, piic):
        piic.add_collection(piic_result)

    processor_mock = Mock()
    processor_mock.build_tasks = Mock(return_value=2)
    processor_mock.detect_chunk = detect
    processor_mock.get_stats = Mock(return_value={})
    processor_cls = Mock(return_value=processor_mock)
    #collection_mock = Mock(return_value=piic)
    # Remove the mark of import fail
    monkeypatch.setattr(mod, "MISSING_MOD", None)
    # Set the processor to be a mock
    monkeypatch.setattr(mod, "PII_EXTRACT_VERSION", "0.4.0")
    monkeypatch.setattr(mod, "PiiProcessor", processor_cls)
    #monkeypatch.setattr(mod, "PiiCollectionBuilder", collection_mock)
    return processor_mock


# -----------------------------------------------------------------------


def test10_constructor(monkeypatch):
    """
    Test constructing the object
    """
    mock = patch_pii_extract(monkeypatch)

    m = mod.MultiPiiTextProcessor(["en", "es"], default_policy="label")
    assert str(m) == "<MultiPiiTextProcessor [#2/4 label]>"

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
    # Prepare the data that will be reported by the extractor
    piic1 = PiiCollectionLoader()
    piic1.load_json(DATADIR / "example-pii.json")
    patch_pii_extract(monkeypatch, piic1)

    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()

    m = mod.MultiPiiTextProcessor(["en", "es"], default_policy="annotate")
    assert str(m) == "<MultiPiiTextProcessor [#2/4 annotate]>"

    with open(DATADIR / "example-trf.txt", encoding="utf-8") as f:
        exp = f.read()

    got = m(src, "en")
    assert exp == got

    # We get the same result for "es", since we have patched detection
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
    assert str(m) == "<MultiPiiTextProcessor [#1/2 annotate]>"

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


def test60_process_piic(monkeypatch):
    """
    Test keep_piic
    """
    # Load the data that will be "extracted"
    piic1 = PiiCollectionLoader()
    piic1.load_json(DATADIR / "example-pii.json")

    # Create a collection builder, fill it with the data, and set it as
    # the result of the extraction process
    piic2 = processor.PiiCollectionBuilder()
    piic2.add_collection(piic1)
    patch_pii_extract(monkeypatch, piic2)


    m = mod.MultiPiiTextProcessor(["en", "es"], default_policy="annotate",
                                  keep_piic=True)

    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()
    m(src, "en")

    piic = m.piic()
    assert len(piic) == 2


def test61_process_piic_nolang(monkeypatch):
    """
    Test keep_piic, non-existing lang
    """
    piic1 = PiiCollectionLoader()
    piic1.load_json(DATADIR / "example-pii.json")
    piic2 = processor.PiiCollectionBuilder()
    piic2.add_collection(piic1)
    patch_pii_extract(monkeypatch, piic2)

    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()

    m = mod.MultiPiiTextProcessor(["en", "es", "zz"], default_policy="annotate",
                                  keep_piic=True)
    m(src, "en")

    m(src, "zz")

    piic = m.piic()
    assert len(piic) == 4


def test70_process_detectors(monkeypatch):
    """
    Test fetching the detectors
    """
    # Load the data that will be "extracted"
    piic1 = PiiCollectionLoader()
    piic1.load_json(DATADIR / "example-pii.json")

    # Create a collection builder, fill it with the data, and set it as
    # the result of the extraction process
    piic2 = processor.PiiCollectionBuilder()
    piic2.add_collection(piic1)
    patch_pii_extract(monkeypatch, piic2)


    m = mod.MultiPiiTextProcessor(["en", "es"], default_policy="annotate",
                                  keep_piic=True)

    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()
    m(src, "en")

    detectors = m.detectors()
    assert len(detectors) == 1
    assert detectors == {1: PiiDetector("PIISA", "PII Mock detector", "0.1.0")}


def test80_process_stats(monkeypatch):
    """
    Test stats
    """
    piic = PiiCollectionLoader()
    piic.load_json(DATADIR / "example-pii.json")
    proc = patch_pii_extract(monkeypatch, piic)

    with open(DATADIR / "example-src.txt", encoding="utf-8") as f:
        src = f.read()

    m = mod.MultiPiiTextProcessor(["en", "es"], default_policy="annotate")
    m(src, "en")

    r = m.stats()
    assert sorted(r.keys()) == ["chunks", "entities", "num", "time"]
    assert r["chunks"] == {"total": {"en": 1}, "pii": {"en": 1}}
    assert proc.get_stats.called
