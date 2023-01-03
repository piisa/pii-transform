"""
Transform documents by replacing PII instances according to a policy
"""

from operator import attrgetter

from typing import Iterable, Dict, List

from pii_data.types import PiiCollection
from pii_data.types.doc import SrcDocument, DocumentChunk, LocalSrcDocument
from pii_data.types.piicollection import PiiChunkIterator

from ..helper import PiiSubstitutionValue


# --------------------------------------------------------------------------


class PiiTransformer:

    def __init__(self, default_policy: str = None, config: Dict = None,
                 debug: bool = False):
        """
         :param default_policy: a default policy value to apply to all entities
            that do not have a specific policy
         :param policy: configurations for transform policy and/or placheholder
        """
        self._debug = debug
        self.subst = PiiSubstitutionValue(default_policy, config)


    def __repr__(self) -> str:
        return "<PiiTransformer>"


    def __call__(self, document: SrcDocument,
                 piic: PiiCollection) -> SrcDocument:
        """
        Replace in a document the passed detected PII values, in accordance
        with the policies that have been set
         :param document: the original document
         :param piic: the list of detected PII instances
         :return: a local document with all replacements done
        """
        pii_it = PiiChunkIterator(piic)

        # Create the output document, and clone all its metadata
        meta = document.metadata
        dtype = meta.get("document", {}).get("type", "sequence")
        out = LocalSrcDocument(dtype)
        out.add_metadata(**meta)

        # Substitute all PII instances in all chunks
        for chunk in document:

            # Construct the new content for the chunk
            output = []
            pos = 0
            for pii in pii_it(chunk.id):
                output += [chunk.data[pos:pii.pos], self.subst(pii)]
                pos = pii.pos + len(pii)
            chunk_data = "".join(output) + chunk.data[pos:]

            # Add the chunk to the output document
            newchunk = DocumentChunk(chunk.id, chunk_data, chunk.context)
            out.add_chunk(newchunk)

        return out
