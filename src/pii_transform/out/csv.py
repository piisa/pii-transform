"""
Write a table document to a CSV file
"""

import csv

from pii_data.helper.exception import InvArgException
from pii_data.helper.io import openfile
from pii_data.types.doc import TableSrcDocument


def write_csv(doc: TableSrcDocument, outname: str, header: bool = True):
    """
    Write a TableSrcDocument as a CSV file
    """

    if not isinstance(doc, TableSrcDocument):
        raise InvArgException("cannot write document '{}' as CSV: not a table",
                              outname)

    with openfile(outname, "w", encoding="utf-8") as f:
        w = csv.writer(f)

        if header:
            colnames = doc.metadata.get("column", {}).get("name")
            if colnames:
                w.writerow(colnames)

        for row in doc.iter_struct():
            w.writerow(row["data"])
