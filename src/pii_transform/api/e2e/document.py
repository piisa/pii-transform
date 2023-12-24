"""
End-to-end PII processing for documents
"""

import sys

from typing import List, Union, Dict

from packaging.version import Version

from pii_data.helper.io import openfile
from pii_data.helper.config import load_config, TYPE_CONFIG_LIST
from pii_data.helper.exception import InvArgException, ProcException
from pii_data.helper.logger import PiiLogger

try:
    from pii_preprocess.loader import DocumentLoader
    from pii_extract.api import PiiProcessor
    from pii_extract.api.file import piic_format, print_stats, print_tasks
    from pii_extract.gather.collection import TYPE_TASKENUM
    from pii_extract import VERSION as PII_EXTRACT_VERSION
    from pii_decide.api import PiiDecider
    MISSING_MOD = None
except ImportError as e:
    MISSING_MOD = str(e)
    DocumentLoader = None
    PiiProcessor = None
    TYPE_TASKENUM = List
    PII_EXTRACT_VERSION = None

from ..transform import PiiTransformer
from ...out import DocumentWriter
from . import defs


def format_policy(name: str, param: str = None) -> Dict:
    """
    Format a policy
      :param name: policy name
      :param param: policy parameter, for policies that require it
    """
    if name == "hash":
        if param is None:
            raise InvArgException("hash policy needs a key")
        return {"name": "hash", "key": param}
    elif name == "custom":
        if param is None:
            raise InvArgException("custom policy needs a template")
        return {"name": "custom", "template": param}
    else:
        return name


def process_document(infile: str, outfile: str, outformat: str = None,
                     piifile: str = None, config: TYPE_CONFIG_LIST = None,
                     lang: str = None, country: List[str] = None,
                     tasks: TYPE_TASKENUM = None, chunk_context: bool = False,
                     default_policy: Union[str, Dict] = None,
                     verbose: int = 0, show_tasks: bool = False,
                     show_stats: bool = False) -> int:
    """
    Process an input document file:
      - detect PII instances
      - transform the detected instances
      - write an output document

     :param infile: input document filename
     :param outfile: output document filename
     :param outformat: output file format
     :param piifile: optional output filename to save the detected PII
     :param config: additional configuration
     :param lang: default working language
     :param country: country(es) to restrict task for
     :param tasks: restrict to an specific set of detection tasks
     :param chunk_context: add contexts to chunks when detecting
     :param default_policy: default transform policy
     :param verbose: verbosity level, if > 0 print out progress messages
     :param show_tasks: print out the list of built tasks
     :param show_stats: print out statistics on detected PII
    """
    if MISSING_MOD is not None:
        raise ProcException("Error: missing package dependency: {}", MISSING_MOD)
    elif Version(PII_EXTRACT_VERSION) < Version(defs.MIN_PII_EXTRACT_VERSION):
        raise ProcException("incompatible pii-extract-base version {}",
                            PII_EXTRACT_VERSION)

    log = PiiLogger(__name__, verbose > 0)

    # Load a configuration, if given
    if config:
        log(". Loading config: %s", config)
        config = load_config(config)
    else:
        config = {}

    # Build transform object
    trf = PiiTransformer(default_policy=default_policy, config=config)

    # Load the document to process
    log(". Loading document: %s", infile)
    loader = DocumentLoader(config=config)
    doc = loader.load(infile)

    # Select working language: from the document or from the command line
    meta = doc.metadata
    lang = meta.get("main_lang") or meta.get("lang") or lang
    if not lang:
        raise InvArgException("no language defined in options or document")

    # Create a PiiProcessor object for PII detection
    log(". Loading task processor")
    proc = PiiProcessor(debug=verbose > 1, languages=lang, config=config)

    # Build the task objects
    log(". Building task objects")
    proc.build_tasks(lang, country, pii=tasks)
    if show_tasks:
        print_tasks([lang], proc, sys.stdout)

    # Process the file to extract PII
    log(". Detecting PII instances")
    piic = proc(doc, chunk_context=chunk_context)

    # Perform decision
    proc = PiiDecider(config=config, debug=verbose > 1)
    piic = proc.decide_doc(piic)

    # Show statistics
    if show_stats:
        print_stats(proc.get_stats(), sys.stdout)

    # Dump detection results to a file
    if piifile:
        log(". Saving detected PII to: %s", piifile)
        fmt = piic_format(piifile)
        with openfile(piifile, "wt") as fout:
            piic.dump(fout, format=fmt)

    # Transform the document
    log(". Transforming PII instances")
    res = trf(doc, piic)

    # Save the transformed document
    log(". Dumping to: %s", outfile)
    out = DocumentWriter(res)
    out.dump(outfile, format=outformat)
