# Provided APIs

This package provides the transform API for document transformation.

The former end-to-end processing APIs are now in the [pii-process] package.


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


[policy]: policies.md
[pii-process]: https://github.com/piisa/pii-process
