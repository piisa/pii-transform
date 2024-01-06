"""
A class to provide substitution values for PiiEntity instances, by creating
synthetic fake values using the Faker package
"""
from functools import lru_cache
from collections import defaultdict
import random

from faker import Faker
from faker.config import AVAILABLE_LOCALES

from typing import Dict, Callable

from pii_data.types import PiiEntity, PiiEntityInfo, PiiEnum
from pii_data.helper.exception import UnimplementedException

try:
    from pii_extract import LANG_ANY
except ImportError:
    LANG_ANY = "any"


# How many entities to keep in cache to be able to reassign the same value
DEFAULT_CACHE_SIZE = 200


# Available countries per language
# COUNTRIES = {
#     'en': ['GB', 'IE', 'IN', 'NZ', 'US'],
#     'es': ['AR', 'CL', 'CO', 'ES', 'MX'],
#     'fr': ['BE', 'CA', 'CH', 'FR'],
#     'de': ['AT', 'CH', 'DE'],
#     'pt': ['BR', 'PT'],
#     'ro': ['RO']
# }


# Faker providers to use, segmented by PII type & locale
# Either a string (naming the method to use from the Faker object) or a callable
PROVIDER = {
    PiiEnum.EMAIL_ADDRESS: "email",
    PiiEnum.PERSON: "name",
    PiiEnum.LOCATION: "city",
    PiiEnum.BANK_ACCOUNT: "bban",
    PiiEnum.CREDIT_CARD: "credit_card_number",
    PiiEnum.PHONE_NUMBER: {
        "en_US": "phone_number",
        "en_CA": "phone_number",
        "en_IN": "phone_number",
        "en_AU": "phone_number",
        "en_GB": "phone_number",
        "en_NZ": "phone_number",
        "en_PH": "mobile_number",
        "es_AR": "phone_number",
        "es_CL": "phone_number",
        "es_CO": "phone_number",
        "es_ES": "phone_number",
        "fr_CH": "phone_number",
        "fr_FR": "phone_number",
        "de_DE": "phone_number",
        "it_IT": "phone_number",
        "pt_BR": "phone_number",
        "pt_PT": "phone_number",
        "ro_RO": "phone_number"
    },
    PiiEnum.GOV_ID: {
        "en_US": "ssn",
        "en_CA": "ssn",
        "en_GB": "ssn",
        "es_MX": "curp",
        "es_ES": "nif",
        "es_CL": "person_rut"
    },
    PiiEnum.IP_ADDRESS: lambda f: f.ipv4(private=True)
}


# -------------------------------------------------------------------------

class SyntheticValue:

    def __init__(self, config: Dict = None, seed: int = None,
                 cache_size: int = None):
        """
         :param config: configuration to use for this module
         :param seed: set random seed
         :param cache_size: size of the LRU cache used to maintain consistency
           in assignments
        """
        if config is None:
            config = {}
        self.faker = {}
        self._countries = defaultdict(list)
        self._locales = set(AVAILABLE_LOCALES)
        for loc in sorted(self._locales):
            if '_' not in loc:
                continue
            lang, country = loc.split('_')
            self._countries[lang].append(country)

        # Prepare the cache
        if cache_size is None:
            cache_size = config.get("cache_size", DEFAULT_CACHE_SIZE)
        self._cache = lru_cache(maxsize=cache_size)(self._fetch_value)

        # Set the random seed, if needed
        self.seed = seed if seed is not None else config.get("seed")
        if self.seed is not None:
            Faker.seed(self.seed)
            random.seed(self.seed)


    def __repr__(self) -> str:
        return "<SyntheticValue>"


    def reset(self):
        """
        Remove elements in the cache
        """
        self._cache.cache_clear()


    def _fetch_value(self, info: PiiEntityInfo, value: str) -> str:
        """
        Select the value to apply from the placeholder database
        """
        # Define lang & country
        lang = info.lang or "en"
        if lang == LANG_ANY:
            lang = "en"
        country = info.country.upper() if info.country else None
        if lang not in self._countries:
            raise UnimplementedException("no countries available for lang: {}",
                                         lang)
        if country not in self._countries[lang]:
            country = random.choice(self._countries[lang])
        faker_loc = f"{lang}_{country}"
        #print("\nINPUT:", info, faker_loc)

        # Find the provider
        provider_name = PROVIDER.get(info.pii)
        if provider_name is None:
            raise UnimplementedException("synthetic policy unavailable for {}",
                                         info.pii.name)
        elif isinstance(provider_name, dict):
            if faker_loc not in provider_name:
                faker_loc = random.choice(list(provider_name))
            provider_name = provider_name[faker_loc]

        #print("=>", faker_loc, provider_name)

        # Find the faker instance we need (or create one)
        if faker_loc not in self.faker:
            self.faker[faker_loc] = Faker(faker_loc)
        faker = self.faker[faker_loc]

        # Look up the provider and execute it
        if isinstance(provider_name, Callable):
            return provider_name(faker)
        else:
            provider = getattr(faker, provider_name)
            return provider()


    def __call__(self, pii: PiiEntity) -> str:
        """
        Return the appropriate placeholder value for a given PiiEntity
        """
        return self._cache(pii.info, pii.fields["value"])
