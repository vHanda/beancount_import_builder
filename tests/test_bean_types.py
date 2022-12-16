from beancount_one_importer.bean_types import *


def test_to_num():
    assert to_num("2.43") == 2.43
    assert to_num("2,43") == 2.43
    assert to_num("2,43 EUR") == 2.43
    assert to_num("2.43 EUR") == 2.43
    assert to_num("EUR 2,43") == 2.43
    assert to_num("EUR 2.43") == 2.43
    assert to_num("5,898.20") == 5898.20
    assert to_num("5.898,20") == 5898.20
    assert to_num("5,898,20") == 589820
    assert to_num("5.898.20") == 589820


def test_to_date():
    assert to_date("2011-02-01") == date(2011, 2, 1)
    assert to_date("44715.0") == date(2022, 6, 3)
    assert to_date("18-Feb-2020") == date(2020, 2, 18)
    assert to_date("2022-04-06 07:39:19") == date(2022, 4, 6)


def test_is_currency():
    assert is_currency("EUR")
    assert is_currency("VUSA2")
    assert is_currency("VUSA 2") == False
