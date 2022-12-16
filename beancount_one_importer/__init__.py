from beancount.core.data import Account, Amount, Posting, Currency, Transaction
from beancount.core import flags
from beancount.core.number import Decimal
from beancount.parser import printer

import beancount.core.data
import beancount.loader
import itertools
import copy
import csv

from datetime import date

from .bean_types import *


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


def fetch_currency_i(parts):
    return fetch_fn_indexes(parts, is_currency)


def fetch_account_i(parts):
    return fetch_fn_indexes(parts, is_account)


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


def parse_txn(input_s):
    r = beancount.loader.load_string(input_s)

    txns = r[0]
    assert len(txns) == 1
    txn = txns[0]

    meta = txn.meta
    meta.pop("filename")
    meta.pop("lineno")
    meta.pop("__tolerances__")

    txn = txn._replace(meta=meta)

    postings = txn.postings
    assert len(postings) == 1

    return txn


def fetch_matches(parts):
    date_args = fetch_date_i(parts)
    narration_args = fetch_str_i(parts)
    payee_args = [-1] + fetch_str_i(parts)
    meta0_args = [-1] + fetch_str_i(parts)
    meta1_args = [-1] + fetch_str_i(parts)
    meta2_args = [-1] + fetch_str_i(parts)
    posting_account_args = fetch_account_i(parts)
    posting_units_numbers_args = fetch_decimal_i(parts)
    posting_units_currency_args = fetch_currency_i(parts)

    return itertools.product(
        date_args,
        narration_args,
        payee_args,
        meta0_args,
        meta1_args,
        meta2_args,
        posting_account_args,
        posting_units_numbers_args,
        posting_units_currency_args,
    )


def build_txn(
    base_txn: Transaction,
    date_arg,
    narration,
    payee,
    meta0,
    meta1,
    meta2,
    posting_account,
    posting_units_number,
    posting_units_currency,
):

    assert isinstance(date_arg, date)
    assert isinstance(narration, str)
    assert isinstance(payee, str) or payee is None
    assert isinstance(meta0, str) or meta0 is None
    assert isinstance(meta1, str) or meta1 is None
    assert isinstance(meta2, str) or meta2 is None
    assert isinstance(posting_units_number, Decimal)
    assert isinstance(posting_units_currency, str)

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

    assert len(txn.postings) == 1
    posting = txn.postings[0]
    posting = posting._replace(account=posting_account)
    posting = posting._replace(
        units=Amount(posting_units_number, posting_units_currency)
    )
    txn = txn._replace(postings=[posting])

    return txn


def fetch_currencies(txn: Transaction):
    return txn.postings[0].units.currency


def fetch_accounts(txn: Transaction):
    return txn.postings[0].account


def anydup(thelist):
    seen = set()
    for x in thelist:
        if x == -1:
            continue
        if x in seen:
            return True
        seen.add(x)
    return False


def build_importer(input_str, output_str):
    base_txn = parse_txn(output_str)
    expected_output = printer.format_entry(base_txn).strip()

    parts = next(csv.reader([input_str.strip()]))
    # parts = [x for x in parts if x != ""]
    # parts = list(dict.fromkeys(parts))
    # Not sure if empty strings and duplicates should be removed

    print(parts)

    parts.append(fetch_currencies(base_txn))
    parts.append(fetch_accounts(base_txn))

    for m in fetch_matches(parts):
        assert len(m) == 9

        if anydup(m):
            continue

        date_arg = to_date(parts[m[0]])
        narration_arg = to_str(parts[m[1]])
        payee_arg = to_str(parts[m[2]]) if m[2] != -1 else None
        meta_0_arg = to_str(parts[m[3]]) if m[3] != -1 else None
        meta_1_arg = to_str(parts[m[4]]) if m[4] != -1 else None
        meta_2_arg = to_str(parts[m[5]]) if m[5] != -1 else None
        posting_account = to_str(parts[m[6]])
        posting_units_number = Decimal(to_str(to_num(parts[m[7]])))
        posting_units_currency = to_str(parts[m[8]])

        if narration_arg == "":
            continue
        if posting_account == "":
            continue
        if posting_units_currency == "":
            continue

        new_txn = build_txn(
            base_txn,
            date_arg,
            narration_arg,
            payee_arg,
            meta_0_arg,
            meta_1_arg,
            meta_2_arg,
            posting_account,
            posting_units_number,
            posting_units_currency,
        )
        actual_output = printer.format_entry(new_txn).strip()
        # print(actual_output)

        if actual_output == expected_output:
            print("Matched")
            print(actual_output)
            print(m)
            return m

    return None


# FIXME: Check which of the 9 arguments are actually used and avoid generating permutations for the rest
# FIXME: Move anydup into fetch_matches
