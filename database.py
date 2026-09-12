import sqlite3
import pandas as pd
import os

DB_NAME = "business.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():

    conn = get_connection()

    sales = pd.read_csv("data/sales.csv")
    inventory = pd.read_csv("data/inventory.csv")
    customers = pd.read_csv("data/customers.csv")

    sales.to_sql(
        "sales",
        conn,
        if_exists="replace",
        index=False
    )

    inventory.to_sql(
        "inventory",
        conn,
        if_exists="replace",
        index=False
    )

    customers.to_sql(
        "customers",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


def load_data():

    conn = get_connection()

    sales = pd.read_sql(
        "SELECT * FROM sales",
        conn
    )

    inventory = pd.read_sql(
        "SELECT * FROM inventory",
        conn
    )

    customers = pd.read_sql(
        "SELECT * FROM customers",
        conn
    )

    conn.close()

    return sales, inventory, customers


def update_stock(product, new_stock):

    conn = get_connection()

    conn.execute(
        "UPDATE inventory SET stock = ? WHERE product = ?",
        (new_stock, product)
    )

    conn.commit()
    conn.close()

def record_sale(product, category, quantity, unit_price, sale_date):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Check current stock
        cursor.execute(
            "SELECT stock FROM inventory WHERE product = ?",
            (product,)
        )

        row = cursor.fetchone()

        if row is None:
            raise ValueError("Product not found in inventory.")

        current_stock = row[0]

        # Prevent selling more than available stock
        if quantity > current_stock:
            raise ValueError(
                f"Insufficient stock. Only {current_stock} units available."
            )

        # Add sale
        cursor.execute(
            """
            INSERT INTO sales
            (date, product, category, quantity, unit_price)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                sale_date,
                product,
                category,
                quantity,
                unit_price
            )
        )

        # Automatically reduce inventory
        cursor.execute(
            """
            UPDATE inventory
            SET stock = stock - ?
            WHERE product = ?
            """,
            (quantity, product)
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if not os.path.exists(DB_NAME):
    initialize_database()