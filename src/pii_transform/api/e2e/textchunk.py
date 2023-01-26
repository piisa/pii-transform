"""
Process raw text buffers
"""

from typing import List, Tuple

from pii_data.helper.config import TYPE_CONFIG_LIST, load_config
from pii_data.helper.exception import ProcException
from pii_data.types import PiiCollection
from pii_data.types.doc import DocumentChunk
from pii_transform.api import PiiTransformer
try:
    from pii_extract.api.processor import PiiProcessor, PiiCollectionBuilder
    from pii_extract.build.collection import TYPE_TASKENUM
    MISSING = None
except ImportError as e:
    MISSING = str(e)
    TYPE_TASKENUM = List
    PiiProcessor = None
    PiiCollectionBuilder = None



class PiiTextProcessor:
    """
    A simple class that performs end2end PII processing on a text buffer
    """

    def __init__(self, lang: str = "en", default_policy: str = "label",
                 config: TYPE_CONFIG_LIST = None, country: List[str] = None,
                 tasks: TYPE_TASKENUM = None, debug: bool = False):
        """
         :param lang: language that text buffers will be in
         :param default_policy: default transformation policy to use
         :param config: configuration(s) to load, in addition to the defaults
         :param country: country(es) to restrict task for
         :param tasks: restrict to an specific set of detection tasks
         :param debug: activate debug output
        """
        if MISSING is not None:
            raise ProcException("missing package dependency: {}", MISSING)
        self.config = load_config(config or [])
        self.lang = lang
        self.policy = default_policy
        self.proc = PiiProcessor(config=self.config, debug=debug)
        self.proc.build_tasks(lang=lang, country=country, pii=tasks)
        self.trf = PiiTransformer(default_policy=default_policy,
                                  config=self.config, debug=debug)


    def __repr__(self) -> str:
        return f"<PiiTextProcessor [{self.policy}]>"


    def process(self, chunk: DocumentChunk) -> Tuple[DocumentChunk, PiiCollection]:
        """
        Process a document chunk: detect PII and transform the PII instances
        found in the chunk, according to the defined policy
          :return: a tuple (output-chunk, collection-of-detected-pii)
        """
        piic = PiiCollectionBuilder(lang=self.lang)
        self.proc.detect_chunk(chunk, piic)
        chunk = self.trf.transform_chunk(chunk, piic)
        return chunk, piic


    def __call__(self, text: str) -> str:
        """
        Process a text buffer: detect PII and transform the PII instances found,
        according to the defined policy
          :return: the trasformed text buffer
        """
        input_chunk = DocumentChunk(id=0, data=text)
        output_chunk, piic = self.process(input_chunk)
        return output_chunk.data
