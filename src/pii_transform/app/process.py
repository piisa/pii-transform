"""
Command-line script to process data and detect PII instances
"""

import sys
import argparse

from typing import List

from pii_data.helper.io import openfile
from pii_data.helper.exception import InvArgException
try:
    from pii_preprocess.loader import DocumentLoader
    from pii_extract.api import PiiProcessor
    from pii_extract.api.file import piic_format
    MISSING = None
except ImportError as e:
    MISSING = str(e)

from .. import VERSION
from ..api import PiiTransformer
from ..helper.substitution import POLICIES
from .transform import Log, get_policy


def process(args: argparse.Namespace):

    log = Log(args.verbose > 0)

    log(". Loading document:", args.infile)
    loader = DocumentLoader()
    doc = loader.load(args.infile)

    log(". Loading task processor")
    proc = PiiProcessor(debug=args.verbose > 1)
    if args.taskfile:
        log(". Adding tasks in file:", args.taskfile)
        proc.add_json_tasks(args.taskfile)

    meta = doc.metadata
    lang = meta.get("main_lang") or meta.get("lang") or args.lang
    if not lang:
        raise InvArgException("no language defined in options or document")

    # Build the task objects
    log(". Building task objects")
    proc.build_tasks(lang, args.country, tasks=args.tasks)

    # Process the file
    log(". Detecting PII instances")
    piic = proc(doc, chunk_context=args.chunk_context)

    # Dump results
    if args.save_pii:
        log(". Saving detected PII to:", args.save_pii)
        fmt = piic_format(args.save_pii)
        with openfile(args.save_pii, "wt") as fout:
            piic.dump(fout, format=fmt)

    # Transform
    log(". Transforming PII instances")
    if args.hash_key and args.default_policy == "hash":
        args.default_policy = {"name": "hash", "key": args.hash_key}
    policy = get_policy(args.policy_file, log)
    trf = PiiTransformer(default_policy=args.default_policy,
                         policy=policy, placeholder_file=args.placeholder_file)
    out = trf(doc, piic)

    log(". Dumping to:", args.outfile)
    out.dump(args.outfile)


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Preprocess, detect & transform source documents (version {VERSION})")

    g0 = parser.add_argument_group("Input/output paths")
    g0.add_argument("infile", help="source document file")
    g0.add_argument("outfile", help="destination document file")

    g1 = parser.add_argument_group("Language specification")
    g1.add_argument("--lang", help="set document language")
    g1.add_argument("--country", nargs="+", help="countries to use")

    g2 = parser.add_argument_group("Task specification")
    g2.add_argument("--tasks", nargs="+", metavar="TASK_TYPE",
                    help="limit the set of pii tasks to include")
    g2.add_argument("--taskfile", nargs="+",
                    help="add all the pii tasks defined in a JSON file")
    g2.add_argument("--save-pii", metavar="FILENAME",
                    help="save detected PII instances to a file")

    g2 = parser.add_argument_group("Extraction options")
    g2.add_argument("--chunk-context", action="store_true",
                    help="when iterating over the document, add chunk contexts")

    g2 = parser.add_argument_group("Transforming options")
    g2.add_argument("--default-policy", choices=POLICIES,
                    help="Apply a default policy to all entities")
    g2.add_argument("--policy-file",
                    help="JSON file with policies to be applied")
    g2.add_argument("--placeholder-file",
                    help="JSON file with substitution values for the placeholder policy")
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
