# Provided API

This package provides the transform API for document transformation.

*Note: the end-to-end processing APIs formerly here are now located in the
[pii-process] package.*


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

# Load the PII that were detected in the document from a dump file
pii = PiiCollectionLoader()
pii.load(pii_filename)

# Start a transformer object
trf = PiiTransformer(default_policy="label")

# Transform
outdoc = trf(doc, pii)

# Save the document to disk
outdoc.dump(outname)
```

The `pii-transform` command-line script performs the same processing.

Note that the module supports only documents in the [PIISA Source Document
format], which contains the document written as a YAML file. To process and
generate documents in other formats, use the [pii-process] package, which
wraps around this one.


[policy]: policies.md
[pii-process]: https://github.com/piisa/pii-process
[PIISA Source Document format]: https://github.com/piisa/pii-data/blob/main/doc/srcdocument.md#file-format
