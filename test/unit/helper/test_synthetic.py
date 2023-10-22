"""
Test the SyntheticValue class
"""

from pii_data.types import PiiEnum, PiiEntity
import pii_transform.helper.synthetic as mod


def test10_constructor():
    """
    Test constructing the object
    """
    m = mod.SyntheticValue()
    assert str(m) == "<SyntheticValue>"


def test11_constructor_file():
    """
    Test constructing the object with specific config
    """
    m = mod.SyntheticValue({"seed": 1234})
    assert str(m) == "<SyntheticValue>"


def test20_value_person():
    """
    Test person value
    """
    m = mod.SyntheticValue({"seed": 12345})

    # No lang, no country
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23)
    assert m(pii) == "Adam Bryan"

    # lang, no country
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23, lang="en")
    assert m(pii) == "Jacob Lee"

    # lang, country
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23, lang="en",
                          country="gb")
    assert m(pii) == "Charlie Wade"

    # Different language
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23, lang="es",
                          country="ar")
    assert m(pii) == "Francisca Perez Morales"

    # Different language, country not available
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23, lang="es",
                          country="NOT")
    assert m(pii) == "Emily Yasna Carvajal Mansilla"

    # Repeat to ensure we get the same (from the cache)
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23)
    assert m(pii) == "Adam Bryan"

    pii = PiiEntity.build(PiiEnum.PERSON, "John Doe", "43", 23)
    assert m(pii) == "Kayla Moore-O'Connell"

    # Clear the cache and repeat
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23)
    m.reset()
    assert m(pii) == "Jarlath MacMullen"


def test30_value_phone():
    """
    Test phone number value
    """
    m = mod.SyntheticValue({"seed": 12345})

    # No lang, no country
    pii = PiiEntity.build(PiiEnum.PHONE_NUMBER, "12345", "43", 23)
    assert m(pii) == "+63813-453-4962"

    # lang, no country
    pii = PiiEntity.build(PiiEnum.PHONE_NUMBER, "123", "43", 23, lang="en")
    assert m(pii) == "(02)64829825"

    # lang, country
    pii = PiiEntity.build(PiiEnum.PHONE_NUMBER, "123", "43", 23,
                          lang="en", country="gb")
    assert m(pii) == "+441632960186"

    pii = PiiEntity.build(PiiEnum.PHONE_NUMBER, "123", "43", 23,
                          lang="es", country="ar")
    assert m(pii) == "+54 15 2123 1355"


def test40_value_email():
    """
    Test email value
    """
    m = mod.SyntheticValue({"seed": 1234})

    # No lang, no country
    pii = PiiEntity.build(PiiEnum.EMAIL_ADDRESS, "me@server.com", "43", 23)
    assert m(pii) == "asuraprasert@example.org"

    # lang, no country
    pii = PiiEntity.build(PiiEnum.EMAIL_ADDRESS, "me@server.com", "43", 23,
                          lang="en")
    assert m(pii) == "powerschristopher@example.com"

    # lang, country
    pii = PiiEntity.build(PiiEnum.EMAIL_ADDRESS, "me@server.com", "43", 23,
                          lang="en", country="gb")
    assert m(pii) == "andrewholland@example.org"

    pii = PiiEntity.build(PiiEnum.EMAIL_ADDRESS, "yo@servidor.ar", "43", 23,
                          lang="es", country="cl")
    assert m(pii) == "susana79@example.com"


def test50_govid_value():
    """
    Test govid value
    """
    m = mod.SyntheticValue({"seed": 1234})

    # No lang, no country
    pii = PiiEntity.build(PiiEnum.GOV_ID, "123456", "43", 23)
    assert m(pii) == "797-57-1915"

    # lang, no country
    pii = PiiEntity.build(PiiEnum.GOV_ID, "123456", "43", 23, lang="en")
    assert m(pii) == "008-12-9540"

    # lang, country
    pii = PiiEntity.build(PiiEnum.GOV_ID, "123456", "43", 23,
                          lang="en", country="gb")
    assert m(pii) == "ZZ 11 53 00 T"

    pii = PiiEntity.build(PiiEnum.GOV_ID, "0000000H", "43", 23,
                          lang="es", country="es")
    assert m(pii) == "78145262W"


def test60_ip_value():
    """
    Test IP address value
    """
    m = mod.SyntheticValue({"seed": 1234})
    pii = PiiEntity.build(PiiEnum.IP_ADDRESS, "123456", "43", 23)
    assert m(pii) == "172.18.230.141"


def test70_credit_card():
    """
    Test Credit Card value
    """
    m = mod.SyntheticValue({"seed": 1234})
    pii = PiiEntity.build(PiiEnum.CREDIT_CARD, "123456", "43", 23)
    assert m(pii) == "30101901153007"


def test80_credit_card():
    """
    Test Bank Account value
    """
    m = mod.SyntheticValue({"seed": 1234})
    pii = PiiEntity.build(PiiEnum.BANK_ACCOUNT, "123456", "43", 23)
    assert m(pii) == "YODA19011530005979"

    pii = PiiEntity.build(PiiEnum.BANK_ACCOUNT, "123456", "43", 23, lang="es")
    assert m(pii) == "OECF10873187191890481475"

    pii = PiiEntity.build(PiiEnum.BANK_ACCOUNT, "123456", "43", 23,
                          lang="es", country="es")
    assert m(pii) == "43378081052762019721"


def test90_location():
    """
    Test location value
    """
    m = mod.SyntheticValue({"seed": 12345})
    pii = PiiEntity.build(PiiEnum.LOCATION, "Toledo", "43", 23)
    assert m(pii) == "Jessica Ville"

    pii = PiiEntity.build(PiiEnum.LOCATION, "Toledo", "43", 23, lang="es")
    assert m(pii) == "San Eloisa los bajos"

    pii = PiiEntity.build(PiiEnum.LOCATION, "Toledo", "43", 23, lang="de")
    assert m(pii) == "Frauenkirchen"
