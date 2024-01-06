"""
The main object performing PII value substitution
"""
import random
import hashlib

from typing import Union, Dict, Callable

from pii_data.helper.exception import InvArgException
from pii_data.types import PiiEnum, PiiEntity

from .. import defs
from .placeholder import PlaceholderValue
from .synthetic import SyntheticValue, PROVIDER as SYNT_PROVIDER


DEFAULT_POLICY = "label"

POLICIES = (
    "passthrough", "redact", "hash", "label", "placeholder",
    "synthetic", "annotate", "custom"
)

TEMPLATES = {
    "passthrough": "{value}",
    "redact": "<PII>",
    "label": "<{type}>",
    "annotate": "<{type}:{value}>"
}


DEFAULT_HASH_SIZE = 16



class Hasher():
    """
    A class to hash PiiEntity instances, adding a key
    """

    def __init__(self, key: str, size: int = None):
        """
         :param key: key to add to the string to feed the hash with
         :param size: number of hexadecimal digits to keep from the hash
        """
        self.key = str(key)
        self.size = int(size) if size is not None else DEFAULT_HASH_SIZE

    def __call__(self, pii: PiiEntity):
        key = self.key + pii.fields["type"] + str(pii.fields["value"])
        bstring = key.encode('utf-8')
        h = hashlib.sha512(bstring).digest()
        return h[:self.size].hex('-', 4)


# -------------------------------------------------------------------------


def policy_target(target: Union[str, PiiEnum]) -> str:
    """
    Compose the name of a policy target
    """
    if isinstance(target, PiiEnum):
        return target.name
    target = str(target).upper()
    if target == 'DEFAULT':
        return "default"
    try:
        return PiiEnum[target].name
    except KeyError:
        raise InvArgException('invalid policy target: PiiEnum not found: {}',
                              target)


class DefaultEmpty(dict):
    """
    A dict that returns an empty string on missing keys
    """
    def __missing__(self, key):
        return ""


class PiiSubstitutionValue:

    def __init__(self, default_policy: Union[str, Dict] = None,
                 config: Dict = None, seed: int = None):
        """
         :param default_policy: a default policy to apply to all entities that
            do not have a specific policy in the configuration
         :param config: configuration to apply
        """
        self._cache = {}
        self._config = config or {}
        cfg = self._config.get(defs.FMT_CONFIG_TRANSFORM) or {}

        # Set the random seed, if needed
        self.seed = seed if seed is not None else cfg.get("seed")
        if self.seed:
            random.seed(self.seed)

        # Build the policy assigner
        self._assign = {"default": self._policy(default_policy or DEFAULT_POLICY)}
        policy = cfg.get("policy")
        if policy is not None:
            for p, v in policy.items():
                self._assign[policy_target(p)] = self._policy(v)


    def __repr__(self) -> str:
        return f"<PiiSubstitutionValue #{len(self._assign)}>"


    def _policy(self, policy: Union[str, Dict]) -> Callable:
        """
        Compose & return a policy process
         :param policy: either a single policy name, or a dictionary defining
           a policy (with at least a "name" field)
        """
        # Ensure we have a valid policy name & dict
        if isinstance(policy, str):
            pname = policy
            policy = {}
        else:
            try:
                pname = policy["name"]
            except Exception as e:
                raise InvArgException("invalid policy value '{}': {}",
                                      policy, e) from e
        if pname not in POLICIES:
            raise InvArgException("unsupported policy: {}", pname)

        # Return the transformation for this policy
        if pname == "placeholder":
            if pname not in self._cache:
                self._cache[pname] = PlaceholderValue(self._config)
            return self._cache[pname]
        elif pname == "synthetic":
            if pname not in self._cache:
                cfg = self._config.get(defs.FMT_CONFIG_TRANSFORM)
                self._cache[pname] = SyntheticValue(cfg, seed=self.seed)
            return self._cache[pname]
        elif pname == "hash":
            try:
                key = policy["key"]
            except KeyError as e:
                raise InvArgException("hash policy needs a key") from e
            return Hasher(key, size=policy.get("size"))
        elif pname == "custom":
            try:
                return policy["template"]
            except (TypeError, KeyError) as e:
                raise InvArgException("custom policy needs a supplied template") from e
        else:
            # a known policy with an available template
            return TEMPLATES[pname]


    def reset(self):
        """
        Reset all caches (i.e. forget all previous substitutions)
        """
        for p in self._assign.values():
            if hasattr(p, "reset"):
                p.reset()


    def __call__(self, pii: PiiEntity) -> str:
        """
        Find the substitution string for an entity, according to the installed
        policies
        """
        # Find the substitution processor.
        # For Synthetic ensure we've got a provider, else use the default
        proc = self._assign.get(pii.fields["type"]) or self._assign["default"]
        if isinstance(proc, SyntheticValue) and pii.info.pii not in SYNT_PROVIDER:
            proc = self._policy(DEFAULT_POLICY)

        # Apply the processor
        if isinstance(proc, str):
            return proc.format_map(DefaultEmpty(pii.asdict()))
        else:
            return proc(pii)
