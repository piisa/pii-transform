
from pathlib import Path

import tempfile
import pytest

from pii_data.helper.exception import InvArgException
from pii_data.types.piicollection import PiiCollectionLoader
from pii_data.types.doc.localdoc import LocalSrcDocumentFile
from pii_transform.api.transform import PiiTransformer
from pii_transform.out import DocumentWriter


DATADIR = Path(__file__).parents[2] / "data"


def load_file(name: str) -> str:
    with open(name, "rt", encoding="utf-8") as f:
        return f.read()


def test10_process_table_csv():
    """
    """
    doc = LocalSrcDocumentFile(DATADIR / "minidoc-example-table-orig.yaml")
    pii = PiiCollectionLoader()
    pii.load_json(DATADIR / "minidoc-example-table-pii.json")
    m = PiiTransformer()
    result = m(doc, pii)
    out = DocumentWriter(result)

    try:
        f = tempfile.NamedTemporaryFile(mode="wt", suffix=".csv", delete=False)
        out.dump(f, format="csv")
        f.close()
        got = load_file(f.name)
    finally:
        Path(f.name).unlink()

    exp = load_file(DATADIR / "minidoc-example-table-repl.csv")
    assert exp == got

def test10_process_table_csv_error():
    """
    """
    doc = LocalSrcDocumentFile(DATADIR / "minidoc-example-tree-orig.yaml")
    pii = PiiCollectionLoader()
    pii.load_json(DATADIR / "minidoc-example-tree-pii.json")
    m = PiiTransformer()
    result = m(doc, pii)
    out = DocumentWriter(result)

    with pytest.raises(InvArgException):
        try:
            f = tempfile.NamedTemporaryFile(mode="wt", delete=False)
            out.dump(f, format="csv")
        finally:
            Path(f.name).unlink()
