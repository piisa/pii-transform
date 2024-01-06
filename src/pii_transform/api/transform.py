"""
Transform documents by replacing PII instances according to a policy
"""
from operator import attrgetter

from typing import Dict, Union

from pii_data.types import PiiCollection, PiiEntity
from pii_data.types.doc import SrcDocument, DocumentChunk, LocalSrcDocument
from pii_data.types.piicollection import PiiChunkIterator
from pii_data.helper.config import load_config
try:
    from pii_decide.defs import ACT_DISCARD
except ImportError:
    ACT_DISCARD = "discard"

from ..helper import PiiSubstitutionValue
from .. import defs

# Reset all assigment caches for each new document
DEFAULT_RESET = "document"


def discard_pii(pii: PiiEntity) -> bool:
    """
    Check if a Pii instance has been marked for removal
    """
    prc = pii.fields.get("process")
    if not prc or prc.get("stage") != "decision":
        return False
    action = prc.get("action")
    return action == ACT_DISCARD

# --------------------------------------------------------------------------


class PiiTransformer:

    def __init__(self, default_policy: Union[str, Dict] = None,
                 config: Dict = None, debug: bool = False):
        """
         :param default_policy: a default policy value to apply to all entities
            that do not have a specific policy
         :param config: object configuration to apply
         :param debug: print out debug messages
        """
        self._debug = debug
        all_config = load_config(config, [defs.FMT_CONFIG_TRANSFORM,
                                          defs.FMT_CONFIG_PLACEHOLDER])
        config = all_config.get(defs.FMT_CONFIG_TRANSFORM) or {}
        self._reset = config.get("reset", DEFAULT_RESET)
        if default_policy is None:
            default_policy = config.get("default_policy")
        self.subst = PiiSubstitutionValue(default_policy, all_config)


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
            if discard_pii(pii):
                continue
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
        if self._reset == "document":
            self.subst.reset()

        pii_it = PiiChunkIterator(piic)

        # Create the output document, and clone all its metadata
        meta = document.metadata
        dtype = meta.get("document", {}).get("type", "sequence")
        out = LocalSrcDocument(dtype)
        out.add_metadata(**meta)

        # Substitute all PII instances in all chunks
        for chunk in document:
            if self._reset == "chunk":
                self.subst.reset()
            newchunk = self.transform_chunk(chunk, pii_it(chunk.id))
            out.add_chunk(newchunk)

        return out
