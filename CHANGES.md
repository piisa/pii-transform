# ChangeLog

# v. 0.6.0
 * workflow changes
     - added pii-decide API in e2e processes
 * functionality improvements
    -  accept output format argument in process_document()
    -  added --out-stats option to multi script
    -  can save table documents to CSV
 * added optional automatic installation with dependencies
 * policy updates
    - added placeholder values for LOCATION
    - added simple (just a city) LOCATION transformation for synthetic policy
 * removed old logger module (now in pii-data)
 * updated faker dependency

## v. 0.5.1
 * fix: pass the language list to PiiProcessor on object construction
 * update dynamic version checking for pii_extract

## v. 0.5.0
 * improve stats gathering: add counts and timings
 * make placeholder policy start randomly on each list of candidates
 * cache placeholder & synthetic objects upon first initialization
 * for synthetic policy, revert to default policy if we cannot find a provider
 * JSONL processing script

## v. 0.4.2
 * fix: wrong piic object in MultiPiiTextProcessor with `keep_piic`

## v. 0.4.0
 * chunk e2e processors improvement
    - number chunks
    - stats() method for PiiTextProcessor & MultiPiiTextProcessor
	- piic() method for MultiPiiTextProcessor

## v. 0.3.1
 * fixed multilang to use the new multilingual capabilities in
   pii-extract-base 0.3.0

## v. 0.3.0
 * "synthetic" policy implemented, using Faker
 * reset behaviour added to object
 * "ignore" action respected
 * MultiPiiTextProcessor object

## v. 0.2.4
 * fix: removed bogus argument in call to detect

## v. 0.2.3
 * added additional constructor options for PiiTextProcessor
 * new method process() for PiiTextProcessor()

## v. 0.2.2
 * fix: process textchunk API correctly for unordered PII collections

## v. 0.2.1
 * fix: policy argument passing to process_document() for policies with options
 * fix: placeholder processing with non-country-specific options
 * fix: substitution templates with missing fields
 * added more placeholder values to config

## v. 0.2.0
 * API for end-to-end processing of raw text buffers
 * Provide a Python API function for end-to-end document processing

## v. 0.1.0
 * initial version
