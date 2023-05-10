"""
Test the PiiSubstitutionValue class
"""

import random
import pytest

from pii_data.helper.exception import InvArgException, UnimplementedException
from pii_data.types import PiiEnum, PiiEntity

from pii_transform import defs
import pii_transform.helper.substitution as mod



# ------------------------------------------------------------------------


def test10_constructor():
    """
    Test constructing the object, default values
    """
    m = mod.PiiSubstitutionValue()
    assert str(m) == "<PiiSubstitutionValue #1>"


def test11_constructor():
    """
    Test constructing the object, set default policy
    """

    for p in ("placeholder", "redact", "label", "annotate"):
        m = mod.PiiSubstitutionValue(default_policy=p)
        assert str(m) == "<PiiSubstitutionValue #1>"

    with pytest.raises(InvArgException):
        mod.PiiSubstitutionValue(default_policy="not a valid policy")

    with pytest.raises(InvArgException):
        mod.PiiSubstitutionValue(default_policy="hash")

    m = mod.PiiSubstitutionValue(default_policy={"name": "hash", "key": 123})
    assert str(m) == "<PiiSubstitutionValue #1>"

    with pytest.raises(InvArgException):
        mod.PiiSubstitutionValue(default_policy="custom")

    m = mod.PiiSubstitutionValue(default_policy={"name": "custom",
                                                 "template": "ABC"})
    assert str(m) == "<PiiSubstitutionValue #1>"

    mod.PiiSubstitutionValue(default_policy="synthetic")
    assert str(m) == "<PiiSubstitutionValue #1>"


def test110_redact():
    """
    Test constructing the object, set redact policy
    """
    m = mod.PiiSubstitutionValue(default_policy="redact")

    for p in (PiiEnum.CREDIT_CARD, PiiEnum.BLOCKCHAIN_ADDRESS, PiiEnum.BANK_ACCOUNT):
        pii = PiiEntity.build(p, "1234 5678", "43", 23)
        assert m(pii) == "<PII>"


def test120_label():
    """
    Test constructing the object, set label policy
    """
    m = mod.PiiSubstitutionValue(default_policy="label")

    for p in (PiiEnum.CREDIT_CARD, PiiEnum.BLOCKCHAIN_ADDRESS, PiiEnum.BANK_ACCOUNT):
        pii = PiiEntity.build(p, "1234 5678", "43", 23)
        assert m(pii) == f"<{p.name}>"


def test130_annotate():
    """
    Test constructing the object, set annotate policy
    """
    m = mod.PiiSubstitutionValue(default_policy="annotate")

    for p in (PiiEnum.CREDIT_CARD, PiiEnum.BLOCKCHAIN_ADDRESS, PiiEnum.BANK_ACCOUNT):
        pii = PiiEntity.build(p, "1234 5678", "43", 23)
        assert m(pii) == f"<{p.name}:1234 5678>"


def test140_custom():
    """
    Test constructing the object, set custom policy
    """
    policy = {"name": "custom", "template": "{type}={value} ({chunkid})"}
    m = mod.PiiSubstitutionValue(default_policy=policy)

    for p in (PiiEnum.CREDIT_CARD, PiiEnum.BLOCKCHAIN_ADDRESS, PiiEnum.BANK_ACCOUNT):
        pii = PiiEntity.build(p, "1234 5678", "43", 23)
        assert m(pii) == f"{p.name}=1234 5678 (43)"


def test141_custom_missing():
    """
    Test constructing the object, set custom policy, missing fields
    """
    policy = {"name": "custom",
              "template": "{type}={value} ({chunkid}) pos={start} <{country}>"}
    m = mod.PiiSubstitutionValue(default_policy=policy)

    for n, p in enumerate((PiiEnum.CREDIT_CARD, PiiEnum.BLOCKCHAIN_ADDRESS,
                           PiiEnum.BANK_ACCOUNT)):
        pii = PiiEntity.build(p, "1234 5678", "43", n)
        assert m(pii) == f"{p.name}=1234 5678 (43) pos={n} <>"


def test150_hash():
    """
    Test constructing the object, set hash policy
    """
    policy = {"name": "hash", "key": "abcde"}
    m = mod.PiiSubstitutionValue(default_policy=policy)

    uc = (
        (PiiEnum.CREDIT_CARD, "9d88a82f-5cd3fca6-fec5af44-71b67293"),
        (PiiEnum.BLOCKCHAIN_ADDRESS, "28634212-2f18d4fc-04ee8744-4a34c8e2"),
        (PiiEnum.PERSON, "ed27c985-3862e8c5-af773237-3220f92b")
    )

    for pii, exp in uc:
        pii = PiiEntity.build(pii, "1234 5678", "43", 23, lang="en")
        assert m(pii) == exp


def test151_hash_short():
    """
    Test constructing the object, set hash policy, short size
    """
    defpolicy = {"name": "hash", "key": "abcde", "size": 10}
    m = mod.PiiSubstitutionValue(default_policy=defpolicy)

    uc = (
        (PiiEnum.CREDIT_CARD, "9d88-a82f5cd3-fca6fec5"),
        (PiiEnum.BLOCKCHAIN_ADDRESS, "2863-42122f18-d4fc04ee"),
        (PiiEnum.PERSON, "ed27-c9853862-e8c5af77")
    )

    for pii, exp in uc:
        pii = PiiEntity.build(pii, "1234 5678", "43", 23, lang="en")
        assert m(pii) == exp


def test160_placeholder():
    """
    Test constructing the object, set placeholder policy
    """
    config = {
        defs.FMT_CONFIG_TRANSFORM: {"seed": 1234}
    }
    m = mod.PiiSubstitutionValue(default_policy="placeholder", config=config)

    uc = (
        (PiiEnum.CREDIT_CARD, "9999 9999 9999 9999"),
        #(PiiEnum.CREDIT_CARD, "0123 0123 0123 0123"),
        (PiiEnum.BLOCKCHAIN_ADDRESS, "mwXvVQ6vgR78utyPnJrBYqRKJzMGzZiQ1v"),
        (PiiEnum.PERSON, "John Doe"),
        (PiiEnum.MEDICAL, "MEDICAL")
    )
    for pii, exp in uc:
        pii = PiiEntity.build(pii, "1234 5678", "43", 23, lang="en")
        assert m(pii) == exp


def test170_passthrough():
    """
    Test constructing the object, set passthrough policy
    """
    m = mod.PiiSubstitutionValue(default_policy="passthrough")

    for p in (PiiEnum.CREDIT_CARD, PiiEnum.BLOCKCHAIN_ADDRESS, PiiEnum.BANK_ACCOUNT):
        pii = PiiEntity.build(p, "1234 5678", "43", 23)
        assert m(pii) == "1234 5678"


def test180_synthetic():
    """
    Test constructing the object, set placeholder policy
    """
    config = {
        defs.FMT_CONFIG_TRANSFORM: {
            "seed": 1234,
            "policy": {
                PiiEnum.BLOCKCHAIN_ADDRESS: "placeholder"
            }
        }
    }
    m = mod.PiiSubstitutionValue(default_policy="synthetic", config=config)

    uc = (
        (PiiEnum.CREDIT_CARD, "30101901153007"),
        (PiiEnum.BLOCKCHAIN_ADDRESS, "mwXvVQ6vgR78utyPnJrBYqRKJzMGzZiQ1v"),
        (PiiEnum.PERSON, "Mrs. Mariah Washington")
    )
    for pii, exp in uc:
        pii = PiiEntity.build(pii, "1234 5678", "43", 23, lang="en")
        assert m(pii) == exp


def test200_policies():
    """
    Test constructing the object, set detailed policy
    """
    config = {
        defs.FMT_CONFIG_TRANSFORM: {
            "policy": {
                PiiEnum.CREDIT_CARD: "redact",
                PiiEnum.PERSON: "annotate"
            }
        }
    }
    m = mod.PiiSubstitutionValue(config=config)

    uc = (
        (PiiEnum.CREDIT_CARD, "<PII>"),
        (PiiEnum.BLOCKCHAIN_ADDRESS, "<BLOCKCHAIN_ADDRESS>"),
        (PiiEnum.PERSON, "<PERSON:1234 5678>")
    )
    for pii, exp in uc:
        pii = PiiEntity.build(pii, "1234 5678", "43", 23, lang="en")
        assert m(pii) == exp


def test210_reset():
    """
    Test resetting policies
    """
    config = {
        defs.FMT_CONFIG_TRANSFORM: {
            "seed": 1234,
            "reset": "collection",
            "default_policy": "redact",
            "policy": {
                PiiEnum.CREDIT_CARD: "placeholder",
                PiiEnum.PERSON: "synthetic"
            }
        }
    }
    m = mod.PiiSubstitutionValue(config=config)

    uc = (
        (PiiEnum.CREDIT_CARD, "9999 9999 9999 9999"),
        #(PiiEnum.CREDIT_CARD, "0123 0123 0123 0123"),
        (PiiEnum.BLOCKCHAIN_ADDRESS, "<BLOCKCHAIN_ADDRESS>"),
        (PiiEnum.PERSON, "Jessica Smith")
    )

    # Substitute
    for pii, exp in uc:
        pii = PiiEntity.build(pii, "1234 5678", "43", 23, lang="en")
        assert m(pii) == exp

    # Repeat. The previois values are cached, so we get the same
    for pii, exp in uc:
        pii = PiiEntity.build(pii, "1234 5678", "43", 23, lang="en")
        assert m(pii) == exp

    # Reset. Now the cache has been cleared, so we might get different values
    m.reset()

    uc = (
        (PiiEnum.CREDIT_CARD, "9999 9999 9999 9999"),
        (PiiEnum.BLOCKCHAIN_ADDRESS, "<BLOCKCHAIN_ADDRESS>"),
        (PiiEnum.PERSON, "Teresa Aguilar")
    )
    for pii, exp in uc:
        pii = PiiEntity.build(pii, "1234 5678", "43", 23, lang="en")
        assert m(pii) == exp
