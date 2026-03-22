import sqlite3
import os

db_path = r"d:\Roshan\Roshan Projects\Shopkart\rrr-shopkart-backend\db.sqlite3"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Verifying api_product table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS api_product (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    price_inr INTEGER NOT NULL,
    category VARCHAR(100) NOT NULL
)
""")

# Sample static data matching front-end fallback lists for offline stability
products = [
    (1, "Men's Denim Jacket", 2499, "Clothing"),
    (2, "Women's Summer Dress", 1899, "Clothing"),
    (3, "Organic Coffee Beans", 799, "Food"),
    (4, "Premium Dark Chocolate", 499, "Food"),
    (5, "Wireless Headphones", 5999, "Electronics"),
    (6, "Smart Watch Series X", 8999, "Electronics"),
]

print("Seeding products...")
cursor.executemany(
    "INSERT OR REPLACE INTO api_product (id, title, price_inr, category) VALUES (?, ?, ?, ?)",
    products
)

conn.commit()
conn.close()
print("Product table check & seed complete.")
