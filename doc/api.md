# Provided APIs

This package provides three different Python APIs, one local to the package and
two for end-to-end processing.


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

This is a [thin wrapper] over the relevant objects in the PIISA libraries

[policy]: policies.md
[its implementation]: ../src/pii_transform/api/e2e/document.py
[thin wrapper]: ../src/pii_transform/api/e2e/textchunk.py
