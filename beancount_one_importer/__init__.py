from beancount.core.data import Account, Amount, Posting, Currency, Transaction, Cost
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
from .codec import *


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


def build_txn(
    base_txn,
    date_arg,
    narration,
    payee,
    meta0,
    meta1,
    meta2,
    posting_account,
    posting_units_number,
    posting_units_currency,
    posting_cost_number,
    posting_cost_currency,
):

    assert isinstance(date_arg, date)
    assert isinstance(narration, str)
    assert isinstance(payee, str) or payee is None
    assert isinstance(meta0, str) or meta0 is None
    assert isinstance(meta1, str) or meta1 is None
    assert isinstance(meta2, str) or meta2 is None
    assert isinstance(posting_account, str)
    assert isinstance(posting_units_number, Decimal)
    assert isinstance(posting_units_currency, str)
    assert isinstance(posting_cost_number, Decimal) or posting_cost_number is None
    assert isinstance(posting_cost_currency, str) or posting_cost_currency is None

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
    if (
        posting.cost != None
        and posting_cost_number != None
        and posting_cost_currency != None
    ):
        posting = posting._replace(
            cost=posting.cost._replace(
                number=posting_cost_number,
                currency=posting_cost_currency,
            )
        )
    txn = txn._replace(postings=[posting])

    return txn


def parse_csv_line(line):
    return next(csv.reader([line.strip()]))


def find_match(parts, expected_val, args, fetch_value_fn):
    if expected_val == None:
        return (-1, None)

    for partsIndex in args:
        arg = fetch_value_fn(parts[partsIndex]) if partsIndex != -1 else None
        if arg == expected_val:
            return (partsIndex, arg)

    return (-1, None)


def get_meta_index(base_txn, i):
    meta_keys = list(base_txn.meta.keys())
    if i >= len(meta_keys):
        return -1
    return base_txn.meta[meta_keys[i]]


def build_importer(input_str, output_str):
    base_txn, dContext = parse_txn(output_str)
    expected_output = serialize_txn(base_txn, dContext)

    parts = parse_csv_line(input_str)

    meta_keys = list(base_txn.meta.keys())
    posting = base_txn.postings[0]

    # FIXME: Avoid reusing an index already used, except for -1

    date_i, date_v = find_match(parts, base_txn.date, fetch_date_i(parts), to_date)
    narration_i, narration_v = find_match(
        parts, base_txn.narration, fetch_str_i(parts), to_str
    )
    payee_i, payee_v = find_match(
        parts, base_txn.payee, [-1] + fetch_str_i(parts), to_str
    )
    meta_0_i, meta_0_v = find_match(
        parts, get_meta_index(base_txn, 0), [-1] + fetch_str_i(parts), to_str
    )
    meta_1_i, meta_1_v = find_match(
        parts, get_meta_index(base_txn, 1), [-1] + fetch_str_i(parts), to_str
    )
    meta_2_i, meta_2_v = find_match(
        parts, get_meta_index(base_txn, 2), [-1] + fetch_str_i(parts), to_str
    )
    posting_account_i, posting_account_v = find_match(
        parts + fetch_accounts(base_txn),
        posting.account,
        fetch_account_i(parts + fetch_accounts(base_txn)),
        to_str,
    )
    posting_units_number_i, posting_units_number_v = find_match(
        parts, posting.units.number, fetch_decimal_i(parts), to_decimal
    )
    posting_units_currency_i, posting_units_currency_v = find_match(
        parts + fetch_currencies(base_txn),
        posting.units.currency,
        fetch_currency_i(parts + fetch_currencies(base_txn)),
        to_str,
    )
    cost = posting.cost
    cost_number = cost.number if cost != None else None
    cost_currency = cost.currency if cost != None else None
    posting_cost_number_i, posting_cost_number_v = find_match(
        parts, cost_number, fetch_decimal_i(parts), to_decimal
    )
    posting_cost_currency_i, posting_cost_currency_v = find_match(
        parts + fetch_currencies(base_txn),
        cost_currency,
        fetch_currency_i(parts + fetch_currencies(base_txn)),
        to_str,
    )

    new_txn = build_txn(
        base_txn,
        date_v,
        narration_v,
        payee_v,
        meta_0_v,
        meta_1_v,
        meta_2_v,
        posting_account_v,
        posting_units_number_v,
        posting_units_currency_v,
        posting_cost_number_v,
        posting_cost_currency_v,
    )
    actual_output = serialize_txn(new_txn, dContext)
    if actual_output != expected_output:
        return None
    match = (
        date_i,
        narration_i,
        payee_i,
        meta_0_i,
        meta_1_i,
        meta_2_i,
        posting_account_i,
        posting_units_number_i,
        posting_units_currency_i,
        posting_cost_number_i,
        posting_cost_currency_i,
    )
    print("Matched")
    print(match)
    return match
