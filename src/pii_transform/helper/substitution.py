import hashlib

from typing import Union, Dict

from pii_data.helper.exception import InvArgException, UnimplementedException
from pii_data.types import PiiEnum, PiiEntity

from .. import defs
from .placeholder import PlaceholderValue


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
    if isinstance(target, PiiEnum):
        return target.name
    target = str(target).upper()
    if target == 'DEFAULT':
        return "default"
    try:
        return PiiEnum[target].name
    except KeyError:
        raise InvArgException('invalid policy target: {}', target)


class DefaultEmpty(dict):
    """
    A dict that returns an emoty string on missing keys
    """
    def __missing__(self, key):
        return ""


class PiiSubstitutionValue:

    def __init__(self, default_policy: Union[str, Dict] = None,
                 config: Dict = None):
        """
         :param policy: a default policy to apply to all entities that do
            not have a specific policy in the configuration
         :param config: configuration to apply
        """
        self._config = config
        self._ph = None

        # Build the policy assigner
        self._assign = {"default": self._policy(default_policy or DEFAULT_POLICY)}
        policy = config.get(defs.FMT_CONFIG_POLICY) if config else None
        if policy is not None:
            for p, v in policy.items():
                self._assign[policy_target(p)] = self._policy(v)


    def __repr__(self) -> str:
        return f"<PiiSubstitutionValue #{len(self._assign)}>"


    def _policy(self, policy: Union[str, Dict]):
        """
        Compose & return a policy process
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
            if self._ph is None:
                self._ph = PlaceholderValue(self._config)
            return self._ph
        elif pname == "hash":
            try:
                key = policy["key"]
            except KeyError as e:
                raise InvArgException("hash policy needs a key") from e
            return Hasher(key, size=policy.get("size"))
        elif pname == "synthetic":
            raise UnimplementedException("synthetic policy not yet implemented")
        elif pname == "custom":
            try:
                return policy["template"]
            except (TypeError, KeyError) as e:
                raise InvArgException("custom policy needs a supplied template") from e
        else:
            # a known policy with an available template
            return TEMPLATES[pname]


    def __call__(self, pii: PiiEntity) -> str:
        """
        Find the substitution string for an entity, according to the installed
        policies
        """
        v = self._assign.get(pii.fields["type"]) or self._assign["default"]
        if isinstance(v, str):
            return v.format_map(DefaultEmpty(pii.asdict()))
        else:
            return v(pii)
