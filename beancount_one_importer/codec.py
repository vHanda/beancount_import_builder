from beancount.core.data import Account, Amount, Posting, Currency, Transaction
from beancount.core import flags
from beancount.core.number import Decimal
from beancount.parser import printer

import beancount.core.data
import beancount.loader


def parse_txn(input_s):
    r = beancount.loader.load_string(input_s, dedent=True)
    dcontext = r[2]["dcontext"]

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

    p = postings[0]
    if p.cost is not None:
        cost = p.cost._replace(date=None)
        p = p._replace(cost=cost)
        txn = txn._replace(postings=[p])

    return txn, dcontext


def serialize_txn(txn, dcontext=None):
    return printer.format_entry(txn, dcontext=dcontext).strip()


def fetch_currencies(txn):
    p = txn.postings[0]
    if p.cost == None:
        return [p.units.currency]
    else:
        return [p.units.currency, p.cost.currency]


def fetch_accounts(txn):
    return [txn.postings[0].account]
