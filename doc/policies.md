# PII transformation policies

This package defines the following policies for the transformation of PII
instances:
 * **passthrough**: the value of the PII instance is left as is
 * **redact**: all pii instances are replaced by a `<PII>` generic string
 * **label**: a PII instance is replaced by its PII _type_, e.g. `<EMAIL_ADDRESS>`
 * **annotate**: replace the PII instance by a `<TYPE:VALUE>` string, i.e.
   include _both_ the PII type and its value
 * **custom**: perform replacement according to a template, [_see below_](#custom)
 * **hash**: replace by a hash made from the entity value plus a key, [_see below_](#hash)
 * **placeholder**: replace with a prototypical value, [_see below_](#placeholder)
 * **synthetic**: substitute by synthetic data, [_see below_](#synthetic)


# Information on specific policies

## custom

This policy needs an additional `template` parameter, which contains a string
that will act as a template to render the replacement.

The template can contain fields of the PII Instance, enclosed in braces. For
instance, a template:

     {type}={value} country={country}

will generate substitutions such as `GOV_ID=2123131331212 country=us`


## hash

The hash policy substitutes the value of a PII Entity by a hash constructed
from concatenating a key + entity type + entity value. Therefore, if using the
same key a given entity will always produce the same hash.

The output is in the form of a hexadecimal string, with dashes for easier
inspection.

This policy has one required and one optional parameter:
 * `key`: _required_, this is a string that will be added to the PII value to
   create the hash
 * `size`: _optional_, the number of hexadecimal characters used for the hash
 
 
## placeholder

The _placeholder_ policy substitutes PII instances for strings that have the
external shape of the PII type, but its contents are clearly _not_ a valid
value. For instance, `0000 0000 0000 0000` for a credit card, or
`redacted.email@hotmail.com` for an email address.

These substitutions are gathered from a placeholder config file. When
assigning a placeholder value, if there is a list of them available, the
module will rotate values from the list, in a circular fashion.

The policy also contains a consistency cache (of configurable size). This is
used to remember the last assignments, so if a PII instance is repeated, it will
get the _same_ assignment.

The cache can be cleared at the end of each document or each chunk, depending
on configuration.


### Placeholder config file

The placeholder file is a JSON file that contains an entry for each PII type.
Under that entry there can be further subdivisions by `language` and 
`country` (if there are no subdivisions, then the values are applied to all 
PII instances of that type).

At each position, a value can be a single string (which is then always
repeated) or a list of strings, which are serially assigned, as mentioned
above. If a PII type has no entry in the placeholder file, the `label` policy
will be used.

If no placeholder file is indicated in the policy, the module uses only the
[default placeholder file].


## synthetic

This policy creates synthetic values using the [Faker] package. It will try to
adjust the characteristics of the created value to the PII language and
country, if possible.

It has a number of mappings to PII Instances to the adequate Faker
provider. If there is no defined provider for a given PII, the package will
use the default policy on it instead.

The same as the [placeholder](#placeholder) policy, this policy also contains a
consistency cache (of configurable size). This is used to remember the last
assignments, so if a PII instance is repeated, it will get the _same_ assignment.

The cache can be cleared at the end of each document or each chunk, depending
on configuration.


[default placeholder file]: ../src/pii_transform/resources/placeholder.json
[Faker]: https://faker.readthedocs.io/en/stable/index.html
