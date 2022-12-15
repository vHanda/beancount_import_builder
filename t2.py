from beancount.core.data import Account, Amount, Posting, Currency, Transaction
from beancount.core import flags
from beancount.core.number import Decimal
from beancount.parser import printer

import beancount.core.data
import itertools

from datetime import date, timedelta

cp = beancount.core.data.create_simple_posting

input_str = "44715.0,44715.0,BIZUM ENVIADO,,-30.0,2097.06"

parts = input_str.split(",")
parts = [x for x in parts if x != ""]
parts = list(dict.fromkeys(parts))

# Not sure if empty strings and duplicates should be removed

print(parts)


def is_str(x):
    return isinstance(x, str) and not is_num(x)


def is_num(x):
    try:
        float(x)
        return True
    except:
        return False


def is_date(x):
    if not is_num(x):
        return False

    x = to_excel_date(float(x))
    if 2000 <= x.year and x.year <= 2025:
        return True

    #
    # 01-Feb-2011
    # 18-06-2022
    # 18/06/2022
    # 2022-06-18
    #
    return False


def to_excel_date(excel_date_number):
    return date(1899, 12, 30) + timedelta(days=excel_date_number)


def fetch_fn_indexes(parts, fn):
    indexes = []
    i = 0
    while i < len(parts):
        if fn(parts[i]):
            indexes.append(i)
        i += 1
    return indexes


def fetch_date_i(parts):
    return fetch_fn_indexes(parts, is_date)


def fetch_decimal_i(parts):
    return fetch_fn_indexes(parts, is_num)


def fetch_str_i(parts):
    return fetch_fn_indexes(parts, is_str)


def fetch_matches(parts):
    return itertools.product(fetch_date_i(parts), fetch_decimal_i(parts), fetch_str_i(parts))


def create_txn(date_arg, str_arg, decimal_arg):
    assert (isinstance(date_arg, date))
    assert (isinstance(str_arg, str))
    assert (isinstance(decimal_arg, Decimal))

    t = Transaction(date=date_arg,
                    meta={},
                    postings=[],
                    flag=flags.FLAG_OKAY,
                    payee=None,
                    narration=str_arg,
                    tags=frozenset(),
                    links=frozenset())
    date_arg = Posting(Account('Assets:Personal:Spain:LaCaixa'),
                       Amount(decimal_arg, "EUR"), None,
                       None,
                       None,
                       None,)

    t.postings.append(date_arg)
    return printer.format_entry(t)


ms = create_txn(date(2022, 6, 3), "BIZUM ENVIADO", Decimal("-30.0"))
for m in fetch_matches(parts):
    ts = create_txn(to_excel_date(
        float(parts[m[0]])), parts[m[2]], Decimal(parts[m[1]]))
    if ts == ms:
        print("Matched")
        print(m)
        print(ts)

# Python check if type is date
print()
print("Expected output")
print(ms)

"""
Operations -
string - to_num (with comma as decimal) - float
string - trim - string
num - abs - num
num - excel_date - Date
num -


State - [ ..... ]


2011-02-01 * Credit Interest Capitalised
  Assets:Personal:India:CanaraBank  787.0 INR

Extracted inputs -
* date
* payee
* account name
* amount


"""
