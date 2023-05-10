"""
Test the get_element/set_element calls
"""


import pii_transform.helper.misc as mod


TEST = {
    "f1": "v1",
    "f2": {
        "g1": 5,
        "g2": 6
    }
}


def test10_get_element():
    """
    Test get_element
    """
    assert mod.get_element(TEST, "f1") == "v1"
    assert mod.get_element(TEST, "f3") is None
    assert mod.get_element(TEST, "f2.g1") == 5
    assert mod.get_element(TEST, ["f3", "f2.g1"]) == 5


def test20_set_element():
    """
    Test set_element
    """
    assert mod.set_element(TEST, "f1", "v2") is True
    assert TEST["f1"] == "v2"


def test30_set_element():
    """
    Test set_element
    """
    assert mod.set_element(TEST, "f2.g2", 9) is True
    assert TEST["f2"]["g2"] == 9


def test40_set_element():
    """
    Test set_element
    """
    assert mod.set_element(TEST, "f2.g3", 9) is False
