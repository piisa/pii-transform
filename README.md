# pii-transform

[![version](https://img.shields.io/pypi/v/pii-transform)](https://pypi.org/project/pii-transform)
[![changelog](https://img.shields.io/badge/change-log-blue)](CHANGES.md)
[![license](https://img.shields.io/pypi/l/pii-transform)](LICENSE)
[![build status](https://github.com/piisa/pii-transform/actions/workflows/pii-transform-pr.yml/badge.svg)](https://github.com/piisa/pii-transform/actions)

This package takes a source document, a collection of detected PII instances,
and transforms the document by replacing the PII instances in the document
with a different representation.

The type of substitution done is defined by [transformation policies].


## Command-line scripts

The package provides three console scripts:

 * `pii-transform` loads a source document & a collection of already-detected
   PII, and produces a transformed document following the required policies.
 * `pii-process` is a full end-to-end script:
    - load a document, from among the formats supported by `pii-preprocess`
	- detects PII instances, according to `pii-extract` and its installed
	  plugins
    - transforms the detected PII instances (according to the indicated policy)
	  and writes out the transformed documennt
 * [`pii-process-jsonl`] is also a full end-to-end script; this one reads
   JSONL files and processes each line as a separate text buffer (possibly in
   different languages), producing a transformed JSONL document
	  
	  
Note that `pii-process` & `pii-process-jsonl` will need additional packages
to be installed:
 * `pii-preprocess` (only for `pii-process`)
 * `pii-extract-base`, together with any available detection plugins, e.g.
   `pii-extract-plg-regex` and/or `pii-extract-plg-presidio`


## API

The same functionality provided by the command-line scripts can also be
accessed via a [Python API]


[transformation policies]: doc/policies.md
[Python API]: doc/api.md
[`pii-process-jsonl`]: doc/jsonl.md
