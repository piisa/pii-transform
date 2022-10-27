"""
A class to provide substitution values for PiiEntity instances, based on a
file containing placeholder names

Properties are:
 * we can specify a different placeholder by PiiEnum type
 * we can also subdivide a PiiEnum type by language, and then by country
 * values can be fixed strings or lists of choices
 * if a choice, they are assigned consecutively to PiiEntity of the same type
 * the chosen value is maintained for subsequent appearances of the same
   PiiInstance (same type & value)
 * the list is rotated as much as needed
"""

from pathlib import Path
import json
from functools import lru_cache
from collections import defaultdict

from typing import Union, List, Tuple

from pii_data.types import PiiEntity
from pii_data.helper.exception import FileException


# How many entities to keep in cache to be able to reassign the same value
DEFAULT_CACHE_SIZE = 200


class PlaceholderValue:

    def __init__(self, file: str = None, cache_size: int = None):
        """
         :param file: JSON file containing placeholder values
         :param cache_size: size of the LRU cache used to maintain consistency
           in assignments
        """

        # Get the file with placeholder values
        if file is None:
            file = Path(__file__).parents[1] / "resources" / "placeholder.json"
        self._phfile = file
        with open(self._phfile, encoding="utf-8") as f:
            try:
                self._values = json.load(f)
            except json.JSONDecodeError as e:
                raise FileException("cannot read JSON file {}: {}",
                                    self._phfile, e) from e

        # Prepare the cache
        if cache_size is None:
            cache_size = DEFAULT_CACHE_SIZE
        self._cache = lru_cache(maxsize=cache_size)(self._rotate_value)
        self._index = defaultdict(int)


    def __repr__(self) -> str:
        return f"<PlaceholderValue: {self._phfile.name}>"


    def _select_value(self, pii: PiiEntity) -> Union[str, List[str]]:
        """
        Select the value to apply from the placeholder database
        """
        fields = pii.fields
        pii_type = fields["type"]
        elem = self._values.get(pii_type)
        if not elem:
            return pii_type
        if isinstance(elem, (list, str)):
            return elem

        lang = elem.get(fields.get("lang")) or elem.get("any")
        if not lang:
            return pii_type
        country = lang.get(fields.get("country")) or lang.get("any")
        return country or pii_type


    def _rotate_value(self, key: str, value: str, choices: Tuple[str]):
        """
        Rotate the value to use from the list, keeping consistency in
        assignments to the same PiiEntity values

        Note: "value" is here only to trigger the LRU cache retrieval
        """
        try:
            return choices[self._index[key]]
        finally:
            self._index[key] = (self._index[key] + 1) % len(choices)


    def __call__(self, pii: PiiEntity) -> str:
        """
        Return the appropriate placeholder value for a given PiiEntity
        """
        # Check the value we have
        value = self._select_value(pii)

        # If it's a single string, just return it
        if isinstance(value, str):
            return value

        # If it's a list, choose the value to use
        fields = pii.fields
        key = '/'.join(str(fields.get(e)) for e in ("type", "lang", "country"))
        return self._cache(key, fields["value"], tuple(value))
