from beancount.core.data import Account, Amount, Posting, Currency, Transaction
from beancount.core import flags
from beancount.core.number import Decimal
from beancount.parser import printer

import beancount.core.data
import beancount.loader


def parse_txn(input_s):
    r = beancount.loader.load_string(input_s, dedent=True)
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


def serialize_txn(txn):
    return printer.format_entry(txn).strip()
