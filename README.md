# pii-transform

This package takes a source document, a collection of detected PII instances,
and transforms the document by replacing the PII instances in the document
with a different representation.

The type of substitution done is defined by [transformation policies].


## Command-line scripts

The package provides two console scripts:

 * `pii-transform` loads a source document & a collection of detected PII, 
   and produces a transformed document following the required policies.
 * `pii-process` is a full end-to-end script:
    - load a document, from among the formats supported by `pii-preprocess`
	- detects PII instances, according to `pii-extract` and its installed
	  plugins
    - transforms the detected PII instances (according to the indicated policy)
	  and writes out the transformed documennt
	  
	  
Note that `pii-process` will need additional packages to be present:
 * `pii-preprocess`
 * `pii-extract-base`, together with any available detection plugins, e.g.
   `pii-extract-plg-regex`


## API

The same functionality provided by the command-line scripts can also be
accessed via a [Python API]

[transformation policies]: doc/policies.md
[Python API]: doc/api.md

