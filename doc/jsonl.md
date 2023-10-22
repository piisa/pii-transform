# pii-process-jsonl

This command-line script is intended to be used for JSONL (aka NDJSON) files, in
which each file line contains a separate document, in JSON format. 

## Usage

The minimum usage is:

     pii-process-jsonl <input-jsonl-file> <output-jsonl-file> --lang <langcode> [<langcode> ..]
	 

## Selecting data in the JSONL file

The base assumption is that the documents in the JSONL lines are JSON objects
that contain _at least_ two fields:
 * The text buffer containing the document to process
 * The language the document is in, as an [ISO 639-1] code
 
The names of those two fields are:
 * The value of the `--field-text` command-line option or, as default, `text`
 * The value of the `--field-lang` command-line option or, as default, `lang`
   or `language`
   
Those two field names can be:
 * multi-valued: a list of values, with will be tried in sequence, the first
   one found in the JSONL document is the one used
 * hierarchical: if a name is a dot-separated string, e.g. `metadata.lang`, 
   then it is understood as a nested dict, and the script will navigate the
   structure to locate the field
   
The remaining fields in the JSONL document will not be used (but will still be
copied over to the output document)


## Language specification

The script has a `--lang` option to indicate the list of languages to be
instantiated for detectors (it should contain a list of [ISO 639-1] 2-letter
language codes). It is therefore needed to know beforehand _the list of languages
the documents in the JSONL file can be in_.

The default value for the language list (if the `--lang` option is not
specified) is to instantiate just English. You can use the
`pii-task-info --list-languages` command to see the list of all languages
with available detectors (this command-line script is part of the
`pii-extract-base` package)

There are two cases in which a document in the JSONL file will not be processed:
 1. If the document defines a language that was not specified in the initial
    language list
 2. If the document does not contain a language specification

In both cases, the document will be copied unmodified to the output, with these
exceptions for case 2:
 * if the `--lang` list supplied to the script contains a single language, it
   will be assumed that this is the document language, and so it will get processed
 * else, if the `--raise-no-lang` option was specified, an exception will be
   raised instead of copying the unmodified document

If one of the languages requested in the `--lang` option is not in the list of
available languages, it means there are no specific detectors available for
it. Documents defining that language will only use the language-independent
detectors (e.g. email addresses, credit card numbers).


## PII output

The option `--out-piic <filename>` will save the collection of all detected
PII instances to either a JSON or JSONL file (depending on the filename
extension).


[ISO 639-1]: https://en.wikipedia.org/wiki/ISO_639-1
