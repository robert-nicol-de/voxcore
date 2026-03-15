import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'demo_database.db')

def create_demo_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
        order_id INTEGER PRIMARY KEY,
        product TEXT,
        category TEXT,
        region TEXT,
        revenue INTEGER,
        order_date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        region TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT,
        category TEXT
    )''')
    # Insert demo data
    c.executemany('INSERT OR IGNORE INTO sales VALUES (?, ?, ?, ?, ?, ?)', [
        (1, 'SmartWatch', 'Wearables', 'West', 1200, '2026-01-05'),
        (2, 'Hiking Boots', 'Outdoor', 'South', 450, '2026-01-07'),
        (3, 'Fitness Tracker', 'Wearables', 'East', 300, '2026-01-09'),
    ])
    c.executemany('INSERT OR IGNORE INTO customers VALUES (?, ?, ?)', [
        (101, 'Summit Retail', 'West'),
        (102, 'Trail Co', 'South'),
    ])
    c.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?)', [
        (1, 'SmartWatch', 'Wearables'),
        (2, 'Hiking Boots', 'Outdoor'),
    ])
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_demo_db()
    print('Demo database created at', DB_PATH)
