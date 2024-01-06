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

import random
from pathlib import Path
from functools import lru_cache
from collections import defaultdict

from typing import Union, List, Tuple, Dict

from pii_data.types import PiiEntity
from pii_data.helper.config import load_single_config, TYPE_CONFIG_LIST
from pii_data.helper.exception import FileException

from .. import defs

# How many entities to keep in cache to be able to reassign the same value
DEFAULT_CACHE_SIZE = 200

# Default filename containing placeholder values
PH_FILENAME = "placeholder.json"


class PlaceholderValue:

    def __init__(self, config: TYPE_CONFIG_LIST = None, cache_size: int = None):
        """
         :param config: a generic PIISA configuration object, or list of them
         :param cache_size: size of the LRU cache used to maintain consistency
           in assignments
        """
        # Get the placeholder default config
        base = Path(__file__).parents[1] / "resources" / PH_FILENAME

        # Load the default config, and add to it the passed one
        config = load_single_config(base, defs.FMT_CONFIG_PLACEHOLDER, config)

        # Get the placeholder values
        try:
            self._values = config["placeholder_values"]
        except KeyError as e:
            raise FileException("cannot fetch placeholder info from config") from e

        # Prepare the cache
        if cache_size is None:
            cache_size = DEFAULT_CACHE_SIZE
        self._cache = lru_cache(maxsize=cache_size)(self._rotate_value)
        self._index = defaultdict(int)


    def __repr__(self) -> str:
        return f"<PlaceholderValue: #{len(self._values)}>"


    def _select_value(self, pii: PiiEntity) -> Union[str, List[str]]:
        """
        Select the value to apply from the placeholder data
        """
        fields = pii.fields
        pii_type = fields["type"]
        elem = self._values.get(pii_type)

        if not elem:
            return pii_type
        if isinstance(elem, (list, str)):
            return elem

        lang = elem.get(pii.info.lang) or elem.get("any")
        if not lang:
            return pii_type
        if isinstance(lang, (list, str)):
            return lang

        country = lang.get(pii.info.country) or lang.get("any")
        return country or pii_type


    def _rotate_value(self, key: str, value: str, choices: Tuple[str]):
        """
        Rotate the value to use from the list, keeping consistency in
        assignments to the same PiiEntity values

        Note: "value" is used as argument only to trigger LRU cache retrieval
        """
        # First time we use this key?
        num_choices = len(choices)
        if key not in self._index:
            self._index[key] = random.randrange(num_choices)

        # Select element & rotate key for next call
        try:
            return choices[self._index[key]]
        finally:
            self._index[key] = (self._index[key] + 1) % num_choices


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
        info = pii.info
        key = '/'.join(map(str, (info.pii, info.lang, info.country)))
        return self._cache(key, pii.fields["value"], tuple(value))
