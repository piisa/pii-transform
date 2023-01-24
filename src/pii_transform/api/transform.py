"""
Transform documents by replacing PII instances according to a policy
"""
from operator import attrgetter

from typing import Dict, Union

from pii_data.types import PiiCollection
from pii_data.types.doc import SrcDocument, DocumentChunk, LocalSrcDocument
from pii_data.types.piicollection import PiiChunkIterator

from ..helper import PiiSubstitutionValue


# --------------------------------------------------------------------------


class PiiTransformer:

    def __init__(self, default_policy: Union[str, Dict] = None,
                 config: Dict = None, debug: bool = False):
        """
         :param default_policy: a default policy value to apply to all entities
            that do not have a specific policy
         :param config: full policy configurations to apply
         :param debug:
        """
        self._debug = debug
        self.subst = PiiSubstitutionValue(default_policy, config)


    def __repr__(self) -> str:
        return "<PiiTransformer>"


    def transform_chunk(self, chunk: DocumentChunk, piic: PiiCollection):
        """
        Perform a transformation on a DocumentChunk
         :param chunk: original chunk
         :param piic: a collection providing the piic for this chunk
        """
        # Construct the new content for the chunk
        output = []
        pos = 0
        for pii in sorted(piic, key=attrgetter("pos")):
            output += [chunk.data[pos:pii.pos], self.subst(pii)]
            pos = pii.pos + len(pii)
        chunk_data = "".join(output) + chunk.data[pos:]
        return DocumentChunk(chunk.id, chunk_data, chunk.context)


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
            newchunk = self.transform_chunk(chunk, pii_it(chunk.id))
            out.add_chunk(newchunk)

        return out
