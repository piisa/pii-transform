"""
Command-line script to process data and detect PII instances
"""

import sys
import argparse

from typing import List

from .. import VERSION
from ..helper.substitution import POLICIES

from ..api.e2e import process_document, format_policy, MISSING_MOD


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
    g2.add_argument("--policy-param",
                    help="policy specific parameter (e.g. hash key, template)")

    g3 = parser.add_argument_group("Other")
    g3.add_argument("--output-format", "-of", choices=("txt", "yaml", "csv"),
                    help="output format")
    g3.add_argument("--verbose","-v", type=int, default=1,
                    help="verbosity level (0-2)")
    g3.add_argument('--reraise', action='store_true',
                    help='re-raise exceptions on errors')
    g3.add_argument("--show-stats", action="store_true", help="show statistics")
    g3.add_argument("--show-tasks", action="store_true", help="show defined tasks")

    return parser.parse_args(args)


def main(args: List[str] = None):
    if MISSING_MOD is not None:
        print("Error: missing package dependency:", MISSING_MOD)
        sys.exit(1)
    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)
    kw = vars(args)
    reraise = kw.pop("reraise")

    try:
        infile = kw.pop("infile")
        outfile = kw.pop("outfile")
        piifile = kw.pop("save_pii")
        outformat = kw.pop("output_format")
        defp = format_policy(kw.pop("default_policy"), kw.pop("policy_param"))
        process_document(infile, outfile, outformat=outformat, piifile=piifile,
                         default_policy=defp, **kw)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if reraise:
            raise
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
