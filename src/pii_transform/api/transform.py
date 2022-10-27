"""
Transform documents by replacing PII instances according to a policy
"""

from operator import attrgetter

from typing import Iterable, Dict, List

from pii_data.types import SrcDocument, PiiCollection, PiiEntity, DocumentChunk
from pii_data.types.localdoc import LocalSrcDocument
from ..helper import PiiSubstitutionValue


# --------------------------------------------------------------------------

class Peeker:
    """
    Wrap an iterable so that we can peek at the next value without retrieving it
    """

    def __init__(self, src: Iterable[str]):
        self.it = iter(src)
        self._get_next()

    def __iter__(self):
        return self

    def _get_next(self):
        """
        Fetch and store the next value
        """
        try:
            self._next = next(self.it)
        except StopIteration:
            self._next = None

    def __next__(self):
        """
        Advance and return the next value
        """
        if self._next is None:
            raise StopIteration()
        try:
            return self._next
        finally:
            self._get_next()

    def peek(self):
        """
        Return the next value without advancing the iterator
        """
        return self._next



class PiiChunkIterator:
    """
    Iterate over the PII collection by groups corresponding to all PiiEntity
    instances for the same document chunk
    """

    def __init__(self, piic: PiiCollection):
        self._piic = Peeker(piic)

    def _chunk_pii(self, chunkid: str) -> Iterable[PiiEntity]:
        """
        Return an iterable over all PiiEntity instances in the collection that
        correspond to the passed chunk id
        """
        chunkid = str(chunkid)
        while True:
            next_pii = self._piic.peek()
            if not next_pii or str(next_pii.fields["chunkid"]) != chunkid:
                return
            yield next(self._piic)

    def __call__(self, chunkid: str) -> List[PiiEntity]:
        """
        Return the list of all PiiEntity instances in the collection that
        correspond to the passed chunk id, sorted by their position in
        the chunk
        """
        return sorted(self._chunk_pii(chunkid), key=attrgetter("pos"))


# --------------------------------------------------------------------------


class PiiTransformer:

    def __init__(self, default_policy: str = None, policy: Dict = None,
                 placeholder_file: str = None, debug: bool = False):
        """
         :param policy: a default policy to apply to all entities that do
            not have a specific policy
         :param policy: a detailed policy per entity type
         :param placeholder_file: a file with values for the placeholder
            policy
        """
        self._debug = debug
        self.subst = PiiSubstitutionValue(default_policy, policy,
                                          placeholder_file=placeholder_file)

    def __repr__(self) -> str:
        return "<PiiTransformer>"


    def __call__(self, document: SrcDocument,
                 piic: PiiCollection) -> SrcDocument:
        """
        Replace in a document the passed detected PII values, in accordance
        with the policies that have been set
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
