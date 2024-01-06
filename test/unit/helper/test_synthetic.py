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
    assert m(pii) == "Patricia Sheridan"

    # lang, no country
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23, lang="en")
    assert m(pii) == "Sarah Huynh"

    # lang, country
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23, lang="en",
                          country="gb")
    assert m(pii) == "Kim Williams-Patel"

    # Different language
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23, lang="es",
                          country="ar")
    assert m(pii) == "Thiago Benjamin Morales"

    # Different language, country not available
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23, lang="es",
                          country="NOT")
    assert m(pii) == "Emily Yasna Carvajal Mansilla"

    # Repeat to ensure we get the same (from the cache)
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23)
    assert m(pii) == "Patricia Sheridan"

    pii = PiiEntity.build(PiiEnum.PERSON, "John Doe", "43", 23)
    assert m(pii) == "Hunar Chauhan"

    # Clear the cache and repeat
    pii = PiiEntity.build(PiiEnum.PERSON, "John Smith", "43", 23)
    m.reset()
    assert m(pii) == "Ian Barrett-Cook"


def test30_value_phone():
    """
    Test phone number value
    """
    m = mod.SyntheticValue({"seed": 12345})

    # No lang, no country
    pii = PiiEntity.build(PiiEnum.PHONE_NUMBER, "12345", "43", 23)
    assert m(pii) == "020 3453496"

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
    assert m(pii) == "fwilson@example.net"

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
    assert m(pii) == "7101901153000597"

    pii = PiiEntity.build(PiiEnum.BANK_ACCOUNT, "123456", "43", 23, lang="es")
    assert m(pii) == "TOEC21087318719189048147"

    pii = PiiEntity.build(PiiEnum.BANK_ACCOUNT, "123456", "43", 23,
                          lang="es", country="es")
    assert m(pii) == "54337808105276201972"


def test90_location():
    """
    Test location value
    """
    m = mod.SyntheticValue({"seed": 12345})
    pii = PiiEntity.build(PiiEnum.LOCATION, "Toledo", "43", 23)
    assert m(pii) == "North Sheridaning"

    pii = PiiEntity.build(PiiEnum.LOCATION, "Toledo", "43", 23, lang="es")
    assert m(pii) == "San Eloisa los bajos"

    pii = PiiEntity.build(PiiEnum.LOCATION, "Toledo", "43", 23, lang="de")
    assert m(pii) == "Frauenkirchen"
