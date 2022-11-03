"""
Test the PlaceholderValue class
"""

from pathlib import Path

from pii_data.types import PiiEnum, PiiEntity
import pii_transform.helper.placeholder as mod


def datafile(name: str) -> str:
    return Path(__file__).parents[2] / "data" / name


def test10_constructor():
    """
    Test constructing the object with default file
    """
    m = mod.PlaceholderValue()
    assert str(m) == "<PlaceholderValue: placeholder.json>"


def test11_constructor_file():
    """
    Test constructing the object with specific file
    """
    m = mod.PlaceholderValue(file=datafile("placeholder-test.json"))
    assert str(m) == "<PlaceholderValue: placeholder-test.json>"


def test20_value():
    """
    Test fixed assignment
    """
    m = mod.PlaceholderValue(file=datafile("placeholder-test.json"))
    pii = PiiEntity(PiiEnum.BITCOIN_ADDRESS, "1234", "43", 23)
    assert m(pii) == "abc"

    pii = PiiEntity(PiiEnum.DISEASE, "1234", "43", 23)
    assert m(pii) == "DISEASE"


def test30_value_rotation():
    """
    Test rotated assignment
    """
    m = mod.PlaceholderValue(file=datafile("placeholder-test.json"))

    pii = PiiEntity(PiiEnum.CREDIT_CARD, "1234 5678", "43", 23)
    assert m(pii) == "0123 0123 0123 0123"

    # Same value -- we get the same placeholder
    pii = PiiEntity(PiiEnum.CREDIT_CARD, "1234 5678", "43", 23)
    assert m(pii) == "0123 0123 0123 0123"

    # Different value
    pii = PiiEntity(PiiEnum.CREDIT_CARD, "1234 567x", "43", 23)
    assert m(pii) == "9999 9999 9999 9999"

    # Again same value -- we get the same placeholder
    pii = PiiEntity(PiiEnum.CREDIT_CARD, "1234 5678", "43", 23)
    assert m(pii) == "0123 0123 0123 0123"

    # Different value
    pii = PiiEntity(PiiEnum.CREDIT_CARD, "1234 567y", "43", 23)
    assert m(pii) == "0000 0000 0000 0000"

    # Different value - rotate back to the first value
    pii = PiiEntity(PiiEnum.CREDIT_CARD, "1234 567z", "43", 23)
    assert m(pii) == "0123 0123 0123 0123"


def test40_value_subdict():
    """
    Test subdict selection
    """
    m = mod.PlaceholderValue(file=datafile("placeholder-test.json"))

    pii = PiiEntity(PiiEnum.PERSON, "Henry James", "43", 23)
    assert m(pii) == "PERSON"

    pii = PiiEntity(PiiEnum.PERSON, "Kurt Vonnegut", "43", 23, lang="en")
    assert m(pii) == "John Doe"

    pii = PiiEntity(PiiEnum.PERSON, "Kurt Vonnegut", "43", 23, lang="en",
                    country="gb")
    assert m(pii) == "Joe Bloggs"

    pii = PiiEntity(PiiEnum.PERSON, "Julio Cortázar", "43", 23, lang="es")
    assert m(pii) == "Fulano Pérez"

    pii = PiiEntity(PiiEnum.PERSON, "Augusto Monterroso", "43", 23, lang="es")
    assert m(pii) == "Mengano de Tal"
