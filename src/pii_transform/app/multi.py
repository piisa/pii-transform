"""
PII end-to-end processing for JSONL files
"""

import argparse
import sys
import json

from typing import List, Dict, Iterable

from pii_data.helper.exception import InvalidDocument, InvArgException
from pii_data.helper.io import openfile, base_extension, load_yaml

from ..api.e2e import MultiPiiTextProcessor
from ..helper.substitution import POLICIES
from ..helper.misc import get_element, set_element
from .. import VERSION


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Preprocess, detect & transform PII on JSONL documents (version {VERSION})")

    g0 = parser.add_argument_group("Input/output paths")
    g0.add_argument("infile", help="JSONL source file")
    g0.add_argument("outfile", help="JSONL destination file")
    g0.add_argument("--out-piic", metavar="OUTFILE",
                    help="output all detected PII instances")
    g0.add_argument("--out-stats", metavar="OUTFILE",
                    help="output statsitics to a JSON file")

    g1 = parser.add_argument_group("Language & data specification")
    g1.add_argument("--lang", nargs='+', default=["en"],
                    help="processing languages (default: %(default)s)")
    g1.add_argument("--field-lang", nargs="+", default=("lang", "language"),
                    help="document field defining the language (default: %(default)s)")
    g1.add_argument("--field-text", default=("text",), nargs="+",
                    help="document field containing the text data (default: %(default)s)")


    g1 = parser.add_argument_group("Process configurations")
    g1.add_argument("--config", nargs="+",
                    help="configuration file(s) to load")
    g1.add_argument("--default-policy", choices=POLICIES,
                    help="Default transformation policy")
    g1.add_argument("--skip-decision", action="store_true",
                    help="Skip the decision step")

    g1 = parser.add_argument_group("Options")
    g1.add_argument("--verbose", "-v", type=int, default=1,
                    help="Print progress messages (0-2, default: %(default)d)")
    g1.add_argument("--raise-no-lang", action='store_true',
                    help="Raise an exception if a document has no language")
    g1.add_argument("--reraise", action='store_true',
                    help="Re-raise on exceptions")

    return parser.parse_args(args)


def read_jsonl(name: str, verbose: bool = False) -> Iterable[Dict]:
    """
    Read a JSONL file and return it line by line
    """
    with openfile(name, encoding="utf-8") as fin:
        for n, line in enumerate(fin, start=1):

            if verbose:
                print(f"# Document: {n}")

            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise InvalidDocument("Error while reading '{}', line {}: {}",
                                      name, n, e) from e


def read_yaml(name: str, verbose: bool = False) -> Iterable[Dict]:
    """
    Read a YAML file assumed to contain a list of dicts, and return it
    item by item
    """
    for n, doc in enumerate(load_yaml(name), start=1):
        if verbose:
            print(f"# Document: {n}")
            yield doc


def piic_format(filename: str, default: str=None) -> str:
    """
    Find out the desired file format for a PII Collection
    """
    ext = base_extension(filename)
    if ext == ".json":
        return "json"
    elif ext in (".ndjson", ".jsonl"):
        return "ndjson"
    elif default:
        return default
    else:
        raise InvArgException("cannot recognize piic output format for: {}",
                              filename)


def process(args: argparse.Namespace):

    #logging.basicConfig(level="INFO")

    if args.verbose:
        print("# Initializing processor for:", ",".join(args.lang))
    proc = MultiPiiTextProcessor(lang=args.lang, config=args.config,
                                 keep_piic=bool(args.out_piic),
                                 default_policy=args.default_policy,
                                 decide=not args.skip_decision,
                                 debug=args.verbose > 1)

    if args.verbose:
        print("# Reading data from:", args.infile)
        print("# Writing data to:", args.outfile)

    # Open source
    src_func = read_yaml if base_extension(args.infile) in (".yml", ".yaml") else read_jsonl
    src = src_func(args.infile, verbose=args.verbose)

    with openfile(args.outfile, "w", encoding="utf-8") as fout:
        for doc in src:

            # Determine language to use
            lang = get_element(doc, args.field_lang) or args.lang
            if isinstance(lang, list) and len(lang) == 1:
                lang = lang[0]

            # Process
            if not lang or not isinstance(lang, str):
                # We cannot process this document, either raise or copy verbatim
                if args.raise_no_lang:
                    raise InvalidDocument("no language specified for document {}", n)
            else:
                text_in = get_element(doc, args.field_text)
                text_out = proc(text_in, lang=lang)
                set_element(doc, args.field_text, text_out)

            # Save transformed document
            json.dump(doc, fout, indent=None, ensure_ascii=False)
            print(file=fout)

    # Output statistics
    if args.verbose or args.out_stats:
        stats = proc.stats()
        if args.verbose:
            print("\n# Statistics:")
            json.dump(stats, sys.stdout, indent=2)
        if args.out_stats:
            with open(args.out_stats, "w") as f:
                json.dump(stats, f, indent=2)

    # Output the collection of PII instances
    if args.out_piic:
        fmt = piic_format(args.out_piic, default="json")
        with openfile(args.out_piic, "w", encoding="utf-8") as f:
            proc.piic().dump(f, format=fmt)


def main(args: List[str] = None):
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)
    try:
        process(args)
    except Exception as e:
        if args.reraise:
            raise
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
