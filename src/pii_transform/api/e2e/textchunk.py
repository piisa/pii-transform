"""
Process raw text buffers
"""

from pii_data.helper.config import TYPE_CONFIG_LIST, load_config
from pii_data.helper.exception import ProcException
from pii_data.types.doc import DocumentChunk
from pii_transform.api import PiiTransformer
try:
    from pii_extract.api.processor import PiiProcessor, PiiCollectionBuilder
    MISSING = None
except ImportError as e:
    PiiProcessor = None
    PiiCollectionBuilder = None
    MISSING = str(e)



class PiiTextProcessor:
    """
    A simple class that performs end2end PII processing on a text buffer
    """

    def __init__(self, lang: str = "en", default_policy: str = "label",
                 config: TYPE_CONFIG_LIST = None):
        """
         :param lang: language that text buffers will be in
         :param default_policy: default transformation policy to use
         :param config: configuration(s) to load, in addition to the defaults
        """
        if MISSING is not None:
            raise ProcException("missing package dependency: {}", MISSING)
        self.config = load_config(config or [])
        self.lang = lang
        self.policy = default_policy
        self.proc = PiiProcessor(config=self.config)
        self.proc.build_tasks(lang=self.lang)
        self.trf = PiiTransformer(default_policy=default_policy,
                                  config=self.config)


    def __repr__(self) -> str:
        return f"<PiiTextProcessor [{self.policy}]>"


    def __call__(self, text: str) -> str:
        """
        Process a text buffer: detect PII and transform the PII instances found,
        according to the defined policy
        """
        chunk = DocumentChunk(id=0, data=text)
        piic = PiiCollectionBuilder(lang=self.lang)
        self.proc.detect_chunk(chunk, piic)
        chunk = self.trf.transform_chunk(chunk, piic)
        return chunk.data
