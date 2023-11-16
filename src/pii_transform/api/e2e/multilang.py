"""
Processor for raw text buffers.
Each buffer can be in a different language.

Requirements: it needs installation of the e2e requirements
"""
from collections import defaultdict
from time import perf_counter

from typing import List, Tuple, Dict, Optional

from packaging.version import Version

from pii_data.helper.config import TYPE_CONFIG_LIST, load_config
from pii_data.helper.exception import ProcException
from pii_data.helper.logger import PiiLogger
from pii_data.types import PiiCollection, PiiDetector
from pii_data.types.doc import DocumentChunk

from .. import PiiTransformer
from . import defs

# Extra PIISA modules we need
try:
    from pii_extract.api.processor import PiiProcessor, PiiCollectionBuilder
    from pii_extract.gather.collection import TYPE_TASKENUM
    from pii_extract import VERSION as PII_EXTRACT_VERSION
    MISSING_MOD = None
except ImportError as e:
    MISSING_MOD = str(e)
    PiiProcessor = None
    PiiCollectionBuilder = None
    TYPE_TASKENUM = List
    PII_EXTRACT_VERSION = None
try:
    from pii_decide.api import PiiDecider
    MISSING_MOD = None
except ImportError as e:
    MISSING_MOD = str(e)
    PiiDecider = None


class MultiPiiTextProcessor:
    """
    A simple class that performs end2end PII processing on text buffers.
    A list of languages can be provided, so that when calling the object, the
    text buffer can be in any of those languages (but only one each time).
    """

    def __init__(self, lang: List[str], default_policy: str = None,
                 config: TYPE_CONFIG_LIST = None, country: List[str] = None,
                 tasks: TYPE_TASKENUM = None, keep_piic: bool = False,
                 decide: bool = True,
                 transform: bool = True, debug: bool = False):
        """
         :param lang: list of languages to be loaded (languages that text buffers
           can be in)
         :param default_policy: default transformation policy to use
         :param config: configuration(s) to load, in addition to the defaults
         :param country: country(es) to restrict task for
         :param tasks: restrict to an specific set of detection tasks
         :param keep_piic: store internally all detected PII
         :param decide: perform PII decision
         :param transform: perform PII transformation
         :param debug: activate debug output
        """
        if MISSING_MOD is not None:
            raise ProcException("missing package dependency: {}", MISSING_MOD)
        elif Version(PII_EXTRACT_VERSION) < Version(defs.MIN_PII_EXTRACT_VERSION):
            raise ProcException("incompatible pii-extract-base version {}",
                                PII_EXTRACT_VERSION)

        self._log = PiiLogger(__name__, debug)
        self._log(". start: lang=%s", lang)
        self._cid = 0
        self._keep_piic = keep_piic
        self._piic = PiiCollectionBuilder()
        self._stats = {
            "chunks": {"total": defaultdict(int), "pii": defaultdict(int)},
            "time": {'detect': 0, 'decide': 0, 'transform': 0},
            "num": {},
            "entities": {}
        }

        self.lang = lang
        self.config = load_config(config or [])
        self.policy = default_policy

        # Build detectors
        self._proc = PiiProcessor(config=self.config, languages=lang, debug=debug)
        num = 0
        for lng in lang:
            ctr = country[lng] if isinstance(country, dict) else country
            self._log(". build-tasks for: %s", lng)
            num += self._proc.build_tasks(lang=lng, country=ctr, pii=tasks)
        self.num_tasks = num

        # Build decider
        if decide:
            self._dec = PiiDecider(config=self.config, debug=debug)
        else:
            self._dec = None

        # Build transformer
        if transform:
            self._trf = PiiTransformer(default_policy=default_policy,
                                       config=self.config, debug=debug)
        else:
            self._trf = None


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

        # Create a new collection and add info about all detectors used so far
        piic = PiiCollectionBuilder(lang=lang)
        piic.add_detectors(self._piic.get_detectors(asdict=False).values())

        # Detect
        s0 = perf_counter()
        self._proc.detect_chunk(chunk, piic)
        s1 = perf_counter()
        self._stats["time"]["detect"] += s1 - s0
        s0 = s1

        # Decide
        if self._dec:
            piic = self._dec.decide_chunk(piic, chunk)
            s1 = perf_counter()
            self._stats["time"]["decide"] += s1 - s0
            s0 = s1

        # Transform
        if self._trf:
            chunk = self._trf.transform_chunk(chunk, piic)
            s1 = perf_counter()
            self._stats["time"]["transform"] += s1 - s0

        self._stats["chunks"]["total"][lang] += 1
        if piic:
            self._stats["chunks"]["pii"][lang] += 1

        # Add data to the general collection
        if self._keep_piic:
            # Add all PII instances
            self._piic.add_collection(piic)
        else:
            # Add only the detectors used
            detectors = piic.get_detectors(asdict=False)
            self._piic.add_detectors(detectors.values())

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
        output_chunk, _ = self.process(input_chunk)
        return output_chunk.data


    def piic(self) -> Optional[PiiCollection]:
        """
        Returns the object with all the detected PII (if it was configured
        to keep it)
        """
        return self._piic if self._keep_piic else None


    def detectors(self) -> Dict[int, PiiDetector]:
        """
        Returns all the detectors that have produced PII instances
        """
        return self._piic.get_detectors(asdict=False)


    def stats(self) -> Dict:
        """
        Returns statistics on the detected & transformed PII instances
        """
        stats = self._stats.copy()
        for k, v in self._proc.get_stats().items():
            stats[k].update(v)
        return stats
