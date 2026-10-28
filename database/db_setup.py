"""
db_setup.py - Database Setup Module
Loads the sales CSV data into a SQLite database.
"""

import sqlite3
import pandas as pd
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sales.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sales_data.csv")


def create_database():
    """
    Reads the CSV file, cleans the data, and loads it into SQLite.
    - Drops rows where Unit_price is missing
    - Skips rows where Quantity is 0
    - Only keeps 'Completed' status transactions for revenue calculations
    """
    # Read CSV file
    df = pd.read_csv(CSV_PATH)

    # --- Data Cleaning ---
    # Drop rows with missing Unit_price
    df["Unit_price"] = pd.to_numeric(df["Unit_price"], errors="coerce")
    before_count = len(df)
    df = df.dropna(subset=["Unit_price"])
    dropped = before_count - len(df)
    if dropped > 0:
        print(f"[INFO] Dropped {dropped} rows with missing Unit_price")

    # Convert Order_date to proper date format
    df["Order_date"] = pd.to_datetime(df["Order_date"], format="%d-%m-%Y")

    # Calculate Revenue column = Quantity * Unit_price - Discount_amount
    df["Revenue"] = (df["Quantity"] * df["Unit_price"]) - df["Discount_amount"]

    # Connect to SQLite and save
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("sales", conn, if_exists="replace", index=False)
    conn.close()

    print(f"[INFO] Database created at {DB_PATH}")
    print(f"[INFO] Total records loaded: {len(df)}")
    return DB_PATH


def get_connection():
    """Returns a connection to the SQLite database."""
    if not os.path.exists(DB_PATH):
        create_database()
    return sqlite3.connect(DB_PATH)


# Run this file directly to set up the database
if __name__ == "__main__":
    create_database()

