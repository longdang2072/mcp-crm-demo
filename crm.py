"""Tiny CRM backed by SQLite. Business logic lives here so it can be tested
without an MCP client."""

import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).with_name("crm.db")

SEED_CUSTOMERS = [
    ("Acme Corp", "billing@acme.example", "USA"),
    ("Blue Ocean Ltd", "hello@blueocean.example", "UK"),
    ("Saigon Coffee Co", "contact@saigoncoffee.example", "Vietnam"),
    ("Nordic Design AB", "info@nordicdesign.example", "Sweden"),
]

SEED_ORDERS = [
    (1, "Website redesign", 1200.0, "paid"),
    (1, "Monthly SEO", 300.0, "pending"),
    (2, "Logo package", 450.0, "paid"),
    (3, "Coffee subscription app", 2500.0, "in_progress"),
]


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            country TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            amount REAL NOT NULL,
            note TEXT,
            issued_on TEXT NOT NULL
        );
        """
    )
    if conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO customers (name, email, country) VALUES (?, ?, ?)",
            SEED_CUSTOMERS,
        )
        conn.executemany(
            "INSERT INTO orders (customer_id, description, amount, status) VALUES (?, ?, ?, ?)",
            SEED_ORDERS,
        )
        conn.commit()


def find_customer(conn: sqlite3.Connection, query: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id, name, email, country FROM customers "
        "WHERE name LIKE ? OR email LIKE ? ORDER BY name",
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    return [dict(r) for r in rows]


def list_orders(conn: sqlite3.Connection, customer_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT id, description, amount, status FROM orders "
        "WHERE customer_id = ? ORDER BY id",
        (customer_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def create_invoice(
    conn: sqlite3.Connection, customer_id: int, amount: float, note: str = ""
) -> dict:
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")
    customer = conn.execute(
        "SELECT name FROM customers WHERE id = ?", (customer_id,)
    ).fetchone()
    if customer is None:
        raise ValueError(f"No customer with id {customer_id}.")
    issued_on = date.today().isoformat()
    cur = conn.execute(
        "INSERT INTO invoices (customer_id, amount, note, issued_on) VALUES (?, ?, ?, ?)",
        (customer_id, amount, note, issued_on),
    )
    conn.commit()
    return {
        "invoice_id": cur.lastrowid,
        "customer": customer["name"],
        "amount": amount,
        "note": note,
        "issued_on": issued_on,
    }
