import sqlite3

import pytest

import crm


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    crm.init_db(c)
    yield c
    c.close()


def test_find_customer(conn):
    results = crm.find_customer(conn, "acme")
    assert len(results) == 1
    assert results[0]["name"] == "Acme Corp"


def test_list_orders(conn):
    orders = crm.list_orders(conn, 1)
    assert [o["description"] for o in orders] == ["Website redesign", "Monthly SEO"]


def test_create_invoice(conn):
    invoice = crm.create_invoice(conn, 1, 500, "Website redesign, final payment")
    assert invoice["customer"] == "Acme Corp"
    assert invoice["amount"] == 500


def test_create_invoice_rejects_bad_input(conn):
    with pytest.raises(ValueError):
        crm.create_invoice(conn, 1, 0)
    with pytest.raises(ValueError):
        crm.create_invoice(conn, 999, 100)
