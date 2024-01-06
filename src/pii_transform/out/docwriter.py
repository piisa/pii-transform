"""
Wrapper clas for writing document to local files
"""

from pii_data.helper.exception import InvArgException
from pii_data.helper.io import base_extension
from pii_data.types.doc import SrcDocument

from .csv import write_csv

def get_fmt(outname: str, format: str) -> str:
    """
    Find out the output format
    """
    ext = base_extension(outname)
    if format is not None:
        return str(format).lower()
    elif ext in (".yml", ".yaml"):
        return "yml"
    elif ext in (".txt", ".text"):
        return "txt"
    elif ext == ".json":
        return "json"
    elif ext == ".csv":
        return "csv"
    else:
        raise InvArgException("unspecified format for: {}", outname)


class DocumentWriter(SrcDocument):

    def __init__(self, doc: SrcDocument):
        self.doc = doc

    def dump(self, outname: str, format: str, **kwargs):
        """
        Write documento to a local file
        """
        fmt = get_fmt(outname, format)

        # Custom writing as CSV (only for table documents)
        if fmt == "csv":
            write_csv(self.doc, outname, header=kwargs.get("header", True))
            return

        # For the remaining formats, use the native dump method
        self.doc.dump(outname, format, **kwargs)
