# Provided APIs

This package provides four different Python APIs, one local to the package and
three for end-to-end processing.


## Transform API

This API takes a document and a set of detected PII instances and performs
_transformations_ in the document, according to the defined [policy]. It is
provided by the `PiiTransformer` class.


```Python
from pii_data.types.piicollection import PiiCollectionLoader
from pii_data.types.doc import LocalSrcDocumentFile
from pii_transform.api import PiiTransformer

# Load a document
doc = LocalSrcDocumentFile(filename)

# Load the PII detected in the document
pii = PiiCollectionLoader()
pii.load(piiname)

# Start a transformer object
trf = PiiTransformer(default_policy="label")

# Transform
outdoc = trf(doc, pii)

# Save to disk
outdoc.dump(outname)
```

The `pii-transform` command-line script performs the same processing.


## Process API

This is an end-to-end process:
 - detect PII instances
 - transform the detected instances
 - write an output document

For it to work the `pii-preprocess` & `pii-extract-base` packages need to
be installed (along with any required detector tasks).

The API is provided by the `process_document` function:

```Python
from pii_transform.api.e2e import process_document

process_document(inputname, outputname)
```

The function accepts many additional arguments to modify the default
behaviour, see [its implementation] for a full list.


The `pii-process` command-line script performs the same processing.



## Process API for text buffers

This is similar to the previous one in that it processes end to end, but it
works with raw text buffers:

```Python
from pii_transform.api.e2e import PiiTextProcessor

# Create the object, defining the language to use and the policy
# Further customization is possible by providing a config
proc = PiiTextProcessor(lang="en", default_policy="label")

# Process a text buffer and get the transformed buffer
outbuf = proc(inbuf)
```

This is a [thin wrapper] over the relevant objects in the PIISA libraries.
The procedure to use it is:
 1. Initialize a `PiiTextProcessor` object, giving as arguments the language
    the text will be in and a default [policy] to apply to transform the
	PII instances found (note that the default config might define other
	policies for specific PII types).
 2. Call the object with a text buffer. It will detect PII instances in it
    and apply the transformation, and will return the transformed text buffer.

Additional process customization is possible by adding a `config` argument to
the constructor. This will contain a PIISA [configuration], or a list of them,
that will be used to modify the behaviour of one or more elements in the
chain. Argument values can be:
 * filenames holding a configuration (in JSON format)
 * in-memory configurations, as a Python dictionary

The constructor contains also additional arguments to select a subset of
detection tasks to apply.


## Multilingual process API for text buffers

There is a small variant over the previous API, the `MultiPiiTextProcessor`
object. This one accepts a _list of languages_ in its constructor; it then
initializes a processor for each of them, and at processing time allows the
selection of language (from among the ones that have been initialized) for
each text buffer to be processed.

```Python
from pii_transform.api.e2e import MultiPiiTextProcessor

# Create the object, defining the languages to use and the default policy
# Further customization is possible by providing a config
proc = MultiPiiTextProcessor(lang=["en", "ch"], default_policy="label")

# Process a text buffer and get the transformed buffer
outbuf1 = proc(inbuf1, lang="en")
outbuf2 = proc(inbuf2, lang="ch")

# Get some statistics on the detected PII
stats = proc.stats()
```

Note that each execution is monolingual, i.e. each text buffer must be in a
_single_ language.

In adition to the default method, which takes a raw text buffer, the object also
contains a `process()` method that takes a [`DocumentChunk`] object.


[policy]: policies.md
[its implementation]: ../src/pii_transform/api/e2e/document.py
[thin wrapper]: ../src/pii_transform/api/e2e/textchunk.py
[configuration]: https://github.com/piisa/piisa/tree/main/docs/configuration.md
[`DocumentChunk`]: https://github.com/piisa/pii-data/blob/main/doc/chunks.md
