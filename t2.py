from beancount.core.data import Account, Amount, Posting, Currency, Transaction
from beancount.core import flags
from beancount.core.number import Decimal
from beancount.parser import printer

import beancount.core.data
import beancount.loader
import itertools
import copy

from datetime import date, timedelta

cp = beancount.core.data.create_simple_posting


def is_str(x):
    return isinstance(x, str) and not is_num(x)


def is_num(x):
    try:
        float(x)
        return True
    except:
        return False


def is_iso_date(x):
    try:
        date.fromisoformat(x)
        return True
    except:
        return False


def is_date(x):
    return is_excel_date(x) or is_iso_date(x)


def is_excel_date(x):
    if not is_num(x):
        return False

    x = to_excel_date(float(x))
    if 1900 <= x.year and x.year <= 2100:
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
    indexes = [-1]
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


"""
Operations -
string - to_num (with comma as decimal) - float
string - trim - string
num - abs - num
num - excel_date - Date
num -

2011-02-01 * Credit Interest Capitalised
  Assets:Personal:India:CanaraBank  787.0 INR

"""


# FIXME: Parse different kinds of dates
# FIXME: Parts different kinds of numbers to amount
# FIXME: Different string matching
# Remove quotes and then case changes
# Trim spaces

# Figure out how to match the currency
# def is_amount(x): "EUR 2,34" "2,34 EUR"


"""
404-7319078-6347502,3 Scale Home Brew Hydrometer Wine Beer Cider Alcohol Testing Making Tester; ,Vishesh Handa,2019-06-24,"EUR 2,34",N/A,N/A,N/A,N/A,

->

Figure out the inputs -
1. Assume everything is an input

For this input, create a function that takes a lot of inputs and creates a transaction

"""


input_s = """
2019-06-24 * "3 Scale Home Brew Hydrometer Wine Beer Cider Alcohol Testing Making Tester;"
  orderId: "404-7319078-6347502"
  Expenses:Personal:Amazon  -2.34 EUR
"""


def parse_txn(input_s):
    r = beancount.loader.load_string(input_s)

    txns = r[0]
    assert (len(txns) == 1)
    txn = txns[0]

    meta = txn.meta
    meta.pop("filename")
    meta.pop("lineno")
    meta.pop('__tolerances__')

    txn = txn._replace(meta=meta)

    postings = txn.postings
    assert (len(postings) == 1)

    return txn


def fetch_matches(parts):
    date_args = fetch_date_i(parts)
    narration_args = fetch_str_i(parts)
    payee_args = fetch_str_i(parts)
    meta0_args = fetch_str_i(parts)
    meta1_args = fetch_str_i(parts)
    meta2_args = fetch_str_i(parts)
    posting_units_numbers_args = fetch_decimal_i(parts)
    posting_units_currency_args = fetch_str_i(parts)

    return itertools.product(date_args, narration_args, payee_args, meta0_args, meta1_args, meta2_args, posting_units_numbers_args, posting_units_currency_args)


# 8 inputs
def build_txn(base_txn: Transaction, date_arg, narration, payee, meta0, meta1, meta2, posting_units_number, posting_units_currency):

    assert (isinstance(date_arg, date))
    assert (isinstance(narration, str))
    assert (isinstance(payee, str) or payee is None)
    assert (isinstance(meta0, str) or meta0 is None)
    assert (isinstance(meta1, str) or meta1 is None)
    assert (isinstance(meta2, str) or meta2 is None)
    assert (isinstance(posting_units_number, Decimal))
    assert (isinstance(posting_units_currency, str))

    txn = copy.deepcopy(base_txn)
    txn = txn._replace(date=date_arg)
    txn = txn._replace(narration=narration)
    txn = txn._replace(payee=payee)

    meta = txn.meta
    meta_i = 0
    for k, v in meta.items():
        if meta_i == 0:
            if meta0 is not None:
                meta[k] = meta0
            else:
                break
        if meta_i == 1:
            if meta1 is not None:
                meta[k] = meta1
            else:
                break

        if meta_i == 2:
            if meta2 is not None:
                meta[k] = meta2
            else:
                break
        meta_i += 1
    txn = txn._replace(meta=meta)

    assert (len(txn.postings) == 1)
    posting = txn.postings[0]
    posting = posting._replace(units=Amount(
        posting_units_number, posting_units_currency))
    txn = txn._replace(postings=[posting])

    return txn


def build_importer(input_str, output_str):
    parts = input_str.strip().split(",")
    # parts = [x for x in parts if x != ""]
    # parts = list(dict.fromkeys(parts))
    parts.append("EUR")

    # Not sure if empty strings and duplicates should be removed

    print(parts)

    base_txn = parse_txn(output_str)
    expected_output = printer.format_entry(base_txn).strip()

    for m in fetch_matches(parts):
        assert (len(m) == 8)

        date_arg = to_excel_date(float(parts[m[0]])) if m[0] != -1 else None
        narration_arg = str(parts[m[1]]) if m[1] != -1 else None
        payee_arg = str(parts[m[2]]) if m[2] != -1 else None
        meta_0_arg = str(parts[m[3]]) if m[3] != -1 else None
        meta_1_arg = str(parts[m[4]]) if m[4] != -1 else None
        meta_2_arg = str(parts[m[5]]) if m[5] != -1 else None
        posting_units_number = Decimal(parts[m[6]]) if m[6] != -1 else None
        posting_units_currency = str(parts[m[7]]) if m[7] != -1 else None

        if date_arg == None:
            continue
        if narration_arg == None:
            continue
        if posting_units_number == None:
            continue
        if posting_units_currency == None or posting_units_currency == "":
            continue
        if ' ' in posting_units_currency:
            continue

        new_txn = build_txn(
            base_txn, date_arg, narration_arg, payee_arg, meta_0_arg, meta_1_arg, meta_2_arg, posting_units_number, posting_units_currency
        )
        actual_output = printer.format_entry(new_txn).strip()

        if actual_output == expected_output:
            print("Matched")
            print(actual_output)
            print(m)
            return m


input_str = "44715.0,44715.0,BIZUM ENVIADO,,-30.0,2097.06"
output_str = """
2022-06-03 * "BIZUM ENVIADO"
    Assets:Personal:Spain:LaCaixa  -30.0 EUR
"""

build_importer(input_str, output_str)
