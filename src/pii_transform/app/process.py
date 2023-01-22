"""
Command-line script to process data and detect PII instances
"""

import sys
import argparse

from typing import List

from pii_data.helper.io import openfile
from pii_data.helper.config import load_config
from pii_data.helper.exception import InvArgException
try:
    from pii_preprocess.loader import DocumentLoader
    from pii_extract.api import PiiProcessor
    from pii_extract.api.file import piic_format, print_stats, print_tasks
    MISSING = None
except ImportError as e:
    MISSING = str(e)

from .. import VERSION
from ..api import PiiTransformer
from ..helper.substitution import POLICIES
from .transform import Log


def process(args: argparse.Namespace):
    """
    The main processing function
    """

    log = Log(args.verbose > 0)

    # Load a configuration, if given
    if args.config:
        log(". Loading config:", args.config)
        config = load_config(args.config)
    else:
        config = {}

    # Load the document to process
    log(". Loading document:", args.infile)
    loader = DocumentLoader(config=config)
    doc = loader.load(args.infile)

    # Select working language: from the document or from the command line
    meta = doc.metadata
    lang = meta.get("main_lang") or meta.get("lang") or args.lang
    if not lang:
        raise InvArgException("no language defined in options or document")

    # Create a PiiProcessor object for PII detection
    log(". Loading task processor")
    proc = PiiProcessor(debug=args.verbose > 1, config=config)

    # Build the task objects
    log(". Building task objects")
    proc.build_tasks(lang, args.country, pii=args.tasks)
    if args.show_tasks:
        print_tasks(lang, proc, sys.stdout)

    # Process the file
    log(". Detecting PII instances")
    piic = proc(doc, chunk_context=args.chunk_context)

    # Show statistics
    if args.show_stats:
        print_stats(proc.get_stats(), sys.stdout)

    # Dump detection results to a file
    if args.save_pii:
        log(". Saving detected PII to:", args.save_pii)
        fmt = piic_format(args.save_pii)
        with openfile(args.save_pii, "wt") as fout:
            piic.dump(fout, format=fmt)

    # Transform the document
    log(". Transforming PII instances")
    if args.hash_key and args.default_policy == "hash":
        args.default_policy = {"name": "hash", "key": args.hash_key}
    trf = PiiTransformer(default_policy=args.default_policy, config=config)
    out = trf(doc, piic)

    # Save the transformed document
    log(". Dumping to:", args.outfile)
    out.dump(args.outfile)


# -------------------------------------------------------------------------


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Preprocess, detect & transform source documents (version {VERSION})")

    g0 = parser.add_argument_group("Input/output paths")
    g0.add_argument("infile", help="source document file")
    g0.add_argument("outfile", help="destination document file")

    g1 = parser.add_argument_group("Language specification")
    g1.add_argument("--lang", help="set document language")
    g1.add_argument("--country", nargs="+", help="countries to use")

    g1 = parser.add_argument_group("Process configurations")
    g1.add_argument("--config", nargs="+",
                    help="configuration file(s) to process")

    g2 = parser.add_argument_group("Task specification")
    g2.add_argument("--tasks", nargs="+", metavar="TASK_TYPE",
                    help="limit the set of pii tasks to include")
    g2.add_argument("--save-pii", metavar="FILENAME",
                    help="save detected PII instances to a file")

    g2 = parser.add_argument_group("Extraction options")
    g2.add_argument("--chunk-context", action="store_true",
                    help="when iterating over the document, add chunk contexts")

    g2 = parser.add_argument_group("Transforming options")
    g2.add_argument("--default-policy", choices=POLICIES,
                    help="Apply a default policy to all entities")
    g2.add_argument("--hash-key",
                    help="key value for the hash policy")

    g3 = parser.add_argument_group("Other")
    g3.add_argument("--verbose","-v", type=int, default=1,
                    help="verbosity level (0-2)")
    g3.add_argument('--reraise', action='store_true',
                    help='re-raise exceptions on errors')
    g3.add_argument("--show-stats", action="store_true", help="show statistics")
    g3.add_argument("--show-tasks", action="store_true", help="show defined tasks")

    return parser.parse_args(args)


def main(args: List[str] = None):
    if MISSING is not None:
        print("Error: missing package dependency:", MISSING)
        sys.exit(1)
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)
    try:
        process(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.reraise:
            raise
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
