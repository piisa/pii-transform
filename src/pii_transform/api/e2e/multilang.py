"""
Multi-language processor for raw text buffers
"""

from typing import List, Tuple, Dict

from packaging.version import Version

from pii_data.helper.config import TYPE_CONFIG_LIST, load_config
from pii_data.helper.exception import ProcException
from pii_data.helper.logger import PiiLogger
from pii_data.types import PiiCollection
from pii_data.types.doc import DocumentChunk
from pii_transform.api import PiiTransformer
try:
    from pii_extract.api.processor import PiiProcessor, PiiCollectionBuilder
    from pii_extract.build.collection import TYPE_TASKENUM
    from pii_extract import VERSION as PII_EXTRACT_VERSION
    MISSING = None
except ImportError as e:
    MISSING = str(e)
    PiiProcessor = None
    PiiCollectionBuilder = None
    TYPE_TASKENUM = List
    PII_EXTRACT_VERSION = None



class MultiPiiTextProcessor:
    """
    A simple class that performs end2end PII processing on a text buffer,
    suitable for a list of languages
    """

    def __init__(self, lang: List[str], default_policy: str = None,
                 config: TYPE_CONFIG_LIST = None, country: List[str] = None,
                 tasks: TYPE_TASKENUM = None, keep_piic: bool = False,
                 debug: bool = False):
        """
         :param lang: list of languages that text buffers can be in
         :param default_policy: default transformation policy to use
         :param config: configuration(s) to load, in addition to the defaults
         :param country: country(es) to restrict task for
         :param tasks: restrict to an specific set of detection tasks
         :param keep_piic: store all detected PII
         :param debug: activate debug output
        """
        if MISSING is not None:
            raise ProcException("missing package dependency: {}", MISSING)
        elif Version(PII_EXTRACT_VERSION) < Version("0.3.1"):
            raise ProcException("incompatible pii-extract-base version {}",
                                PII_EXTRACT_VERSION)

        self._log = PiiLogger(__name__, debug)
        self._log(". start: lang=%s", lang)
        self._cid = 0
        self.config = load_config(config or [])
        self.policy = default_policy
        self.lang = lang
        self._proc = PiiProcessor(config=self.config, debug=debug)
        self._piic = PiiCollectionBuilder() if keep_piic else None
        num = 0
        for lng in lang:
            ctr = country[lng] if isinstance(country, dict) else country
            self._log(". build-tasks for: %s", lng)
            num += self._proc.build_tasks(lang=lng, country=ctr, pii=tasks)
        self._trf = PiiTransformer(default_policy=default_policy,
                                   config=self.config, debug=debug)
        self.num_tasks = num


    def __repr__(self) -> str:
        return f"<MultiPiiTextProcessor [#{len(self.lang)}/{self.num_tasks} {self.policy}]>"


    def process(self, chunk: DocumentChunk) -> Tuple[DocumentChunk, PiiCollection]:
        """
        Process a document chunk: detect PII and transform the PII instances
        found in the chunk, according to the defined policy
          :return: a tuple (output-chunk, collection-of-detected-pii)
        """
        try:
            lang = chunk.context["lang"]
        except (KeyError, TypeError):
            raise ProcException("missing chunk language")

        piic = self._piic if self._piic is not None else PiiCollectionBuilder(lang=lang)
        self._proc.detect_chunk(chunk, piic)
        chunk = self._trf.transform_chunk(chunk, piic)
        return chunk, piic


    def __call__(self, text: str, lang: str) -> str:
        """
        Process a text buffer: detect PII and transform the PII instances found,
        according to the defined policy
          :param text: text buffer
          :param lang: text language
          :return: the trasformed text buffer
        """
        self._cid += 1
        input_chunk = DocumentChunk(id=self._cid, data=text,
                                    context={"lang": lang})
        output_chunk, piic = self.process(input_chunk)
        return output_chunk.data


    def piic(self) -> PiiCollection:
        """
        Returns the object with all detected PII (if configured)
        """
        return self._piic


    def stats(self) -> Dict:
        """
        Returns statistics on the detected PII instances
        """
        return self._proc.get_stats()
