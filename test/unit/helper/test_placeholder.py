"""
Test the PlaceholderValue class
"""

from pathlib import Path

from pii_data.types import PiiEnum, PiiEntity
from pii_data.helper.config import load_config
import pii_transform.helper.placeholder as mod


def datafile(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name


def test10_constructor():
    """
    Test constructing the object with default file
    """
    m = mod.PlaceholderValue()
    assert str(m) == "<PlaceholderValue: #5>"


def test11_constructor_file():
    """
    Test constructing the object with specific config file
    """
    m = mod.PlaceholderValue(config=datafile("placeholder-test.json"))
    assert str(m) == "<PlaceholderValue: #6>"


def test12_constructor_data():
    """
    Test constructing the object with specific config data
    """
    config = load_config(datafile("placeholder-test.json"))
    m = mod.PlaceholderValue(config=config)
    assert str(m) == "<PlaceholderValue: #6>"


def test20_value():
    """
    Test fixed assignment
    """
    m = mod.PlaceholderValue(config=datafile("placeholder-test.json"))
    pii = PiiEntity.build(PiiEnum.BLOCKCHAIN_ADDRESS, "1234", "43", 23)
    assert m(pii) == "abc"

    pii = PiiEntity.build(PiiEnum.MEDICAL, "1234", "43", 23)
    assert m(pii) == "MEDICAL"


def test30_value_rotation():
    """
    Test rotated assignment
    """
    m = mod.PlaceholderValue(config=datafile("placeholder-test.json"))

    pii = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234 5678", "43", 23)
    assert m(pii) == "0123 0123 0123 0123"

    # Same value -- we get the same placeholder
    pii = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234 5678", "43", 23)
    assert m(pii) == "0123 0123 0123 0123"

    # Different value
    pii = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234 567x", "43", 23)
    assert m(pii) == "9999 9999 9999 9999"

    # Again same value -- we get the same placeholder
    pii = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234 5678", "43", 23)
    assert m(pii) == "0123 0123 0123 0123"

    # Different value
    pii = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234 567y", "43", 23)
    assert m(pii) == "0000 0000 0000 0000"

    # Different value - rotate back to the first value
    pii = PiiEntity.build(PiiEnum.CREDIT_CARD, "1234 567z", "43", 23)
    assert m(pii) == "0123 0123 0123 0123"


def test40_value_subdict():
    """
    Test subdict selection
    """
    m = mod.PlaceholderValue(config=datafile("placeholder-test.json"))

    pii = PiiEntity.build(PiiEnum.PERSON, "Henry James", "43", 23)
    assert m(pii) == "PERSON"

    pii = PiiEntity.build(PiiEnum.PERSON, "Kurt Vonnegut", "43", 23, lang="en")
    assert m(pii) == "John Doe"

    pii = PiiEntity.build(PiiEnum.PERSON, "Kurt Vonnegut", "43", 23, lang="en",
                          country="gb")
    assert m(pii) == "Joe Bloggs"

    pii = PiiEntity.build(PiiEnum.PERSON, "Julio Cortázar", "43", 23, lang="es")
    assert m(pii) == "Fulano Pérez"

    pii = PiiEntity.build(PiiEnum.PERSON, "Augusto Monterroso", "43", 23,
                          lang="es")
    assert m(pii) == "Mengano de Tal"
