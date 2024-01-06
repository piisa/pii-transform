"""
Command-line script to process data and perform PII substitutions
"""

import sys
import argparse

from typing import List

from pii_data.types.piicollection import PiiCollectionLoader
from pii_data.types.doc import LocalSrcDocumentFile

from .. import VERSION
from ..helper.substitution import POLICIES
from ..api import PiiTransformer
from ..out import DocumentWriter

class Log:
    """
    A very simple class to conditionally log messages to console_scripts
    """
    def __init__(self, verbose: bool):
        self._v = verbose

    def __call__(self, msg: str, *args):
        if self._v:
            print(msg, *args, file=sys.stderr)


def process(args: argparse.Namespace):

    log = Log(args.verbose)

    if args.hash_key and args.default_policy == "hash":
        args.default_policy = {"name": "hash", "key": args.hash_key}
    if args.config:
        log(". Using config:", args.config)
    trf = PiiTransformer(default_policy=args.default_policy, config=args.config)

    log(". Loading document:", args.infile)
    doc = LocalSrcDocumentFile(args.infile)

    log(". Loading Pii collection:", args.pii)
    pii = PiiCollectionLoader()
    pii.load(args.pii)

    log(". Processing")
    res = trf(doc, pii)

    log(". Dumping to:", args.outfile)
    out = DocumentWriter(res)
    out.dump(args.outfile, format=args.output_format)



def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Transform detected PII instances in a document (version {VERSION})")

    g0 = parser.add_argument_group("Input/output paths")
    g0.add_argument("infile", help="source document file (YAML)")
    g0.add_argument("pii", help="detected PII instances (YAML, JSON)")
    g0.add_argument("outfile", help="destination document file")

    g2 = parser.add_argument_group("Processing options")
    g2.add_argument("--default-policy", choices=POLICIES,
                    help="Apply a default policy to all entities")
    g2.add_argument("--config", nargs="+",
                    help="Configuration file for policies and/or placeholder")
    g2.add_argument("--hash-key",
                    help="key value for the hash policy")
    g2.add_argument("--output-format", "-of", choices=("txt", "yaml", "csv"),
                    help="output format")

    g3 = parser.add_argument_group("Other")
    g3.add_argument("-q", "--quiet", action="store_false", dest="verbose")
    g3.add_argument('--reraise', action='store_true',
                    help='re-raise exceptions on errors')
    g3.add_argument("--show-stats", action="store_true", help="show statistics")
    g3.add_argument("--show-tasks", action="store_true", help="show defined tasks")

    return parser.parse_args(args)


def main(args: List[str] = None):
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
