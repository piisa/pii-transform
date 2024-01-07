# pii-transform

[![version](https://img.shields.io/pypi/v/pii-transform)](https://pypi.org/project/pii-transform)
[![changelog](https://img.shields.io/badge/change-log-blue)](CHANGES.md)
[![license](https://img.shields.io/pypi/l/pii-transform)](LICENSE)
[![build status](https://github.com/piisa/pii-transform/actions/workflows/pii-transform-pr.yml/badge.svg)](https://github.com/piisa/pii-transform/actions)


This package takes a source document, a collection of detected PII instances,
and transforms the document by replacing the PII instances in the document
with a different representation.

The type of substitution done is defined by [transformation policies].

Note: `pii-transform` does **not** implement or use Transformer models for PII
purposes (for the extraction of PII Instances using Transformer models, see
[pii-extract-plg-transformers] or [pii-extract-plg-presidio]).

## Command-line script

The package provides a console script: `pii-transform` loads a source document
& a collection of already-detected


   PII, and produces a transformed document following the required policies.
 * `pii-process` is a full end-to-end script:
    - loads a document, from among the formats supported by `pii-preprocess`
	- detects PII instances, according to `pii-extract` and its installed
	  plugins
    - transforms the detected PII instances (according to the indicated policy)
	  and writes out the transformed documennt
 * [`pii-process-jsonl`] is also a full end-to-end script; this one reads
   `[JSONL] files and processes each line as a separate text buffer (possibly in
   different languages), producing a transformed JSONL document
	  

## API

The same functionality provided by the command-line script can also be
accessed via a [Python API]


## End-to-end workflow

The end-to-end scripts and APIs have been migrated; they are now in the
[`pii-process`] package



[transformation policies]: doc/policies.md
[Python API]: doc/api.md
[`pii-process`]: https://github.com/piisa/pii-process
[pii-extract-plg-transformers]: https://github.com/piisa/pii-extract-plg-transformers
[pii-extract-plg-presidio]: https://github.com/piisa/pii-extract-plg-presidio
