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

## Command-line scripts

The package provides three console scripts:

 * `pii-transform` loads a source document & a collection of already-detected
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
	  
	  
## end-to-end installation

Note that `pii-process` & `pii-process-jsonl` will need additional packages
to be installed:
 * `pii-preprocess` (only when using `pii-process`)
 * `pii-extract-base`, together with any desired detection plugins, e.g.
   `pii-extract-plg-regex`, `pii-extract-plg-transformers`,
   and/or `pii-extract-plg-presidio`
 * `pii-decide`

This installation can be performed explicitly, choosing the packages & plugins
to install. There is also an automatic dependency installation, which
installs a default set of packages, by adding the `[e2e]` qualifier upon
installation of this package, i.e.:

          pip install pii-transform[e2e]

... and this will install `pii_preprocess`, `pii-extract-base`,
`pii-extract-plg-regex`, `pii-extract-plg-transformers` and `pii-decide`

Note that you will also need to install Pytorch, so that the models used by
the `pii-extract-plg-transformers` package can run. See the [transformers
plugin documentation] for more information,


## API

The same functionality provided by the command-line scripts can also be
accessed via a [Python API]



[transformation policies]: doc/policies.md
[Python API]: doc/api.md
[`pii-process-jsonl`]: doc/jsonl.md
[pii-extract-plg-transformers]: https://github.com/piisa/pii-extract-plg-transformers
[pii-extract-plg-presidio]: https://github.com/piisa/pii-extract-plg-presidio
[transformers plugin documentation]: https://github.com/piisa/pii-extract-plg-transformers
[JSONL]: https://jsonlines.org
