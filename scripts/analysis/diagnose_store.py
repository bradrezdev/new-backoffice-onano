import sqlite3
import csv
import os

DB_PATH = 'reflex.db'
CSV_PATH = 'nn_protect_products.csv'

def get_db_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database {DB_PATH} not found.")
        return None
    return sqlite3.connect(DB_PATH)

def check_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables found: {tables}")
    return tables

def check_products(conn, table_name='products'):
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Product count in '{table_name}': {count}")
        return count
    except sqlite3.OperationalError:
        print(f"Table '{table_name}' does not exist (or error accessing it).")
        return -1

def seed_products(conn, table_name='products'):
    print("Seeding products from CSV...")
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV {CSV_PATH} not found.")
        return

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products = list(reader)
    
    if not products:
        print("CSV is empty.")
        return

    cursor = conn.cursor()
    
    # Get columns from DB to match CSV
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    db_columns = [col[1] for col in columns_info]
    
    inserted_count = 0
    for p in products:
        # Filter keys that exist in DB columns
        valid_p = {k: v for k, v in p.items() if k in db_columns}
        
        # Handle booleans/types if necessary (sqlite is flexible but good to be careful)
        # Assuming simple mapping for now.
        
        cols = ', '.join(valid_p.keys())
        placeholders = ', '.join(['?'] * len(valid_p))
        values = list(valid_p.values())
        
        sql = f"INSERT OR IGNORE INTO {table_name} ({cols}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        inserted_count += 1
        
    conn.commit()
    print(f"Seeded {inserted_count} products.")

def check_user_country(conn, user_id=1, table_name='users'):
    cursor = conn.cursor()
    try:
        # Check if user exists
        cursor.execute(f"SELECT id, first_name, email_cache, country_cache FROM {table_name} WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"User ID {user_id} not found.")
            # Verify if there are ANY users
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_users = cursor.fetchone()[0]
            print(f"Total users in DB: {total_users}")
            return
            
        print(f"User ID {user_id} found: Name={user[1]}, Email={user[2]}, Country={user[3]}")
        
        if not user[3]: # Country is None or empty
            print("User has no country. Fixing...")
            cursor.execute(f"UPDATE {table_name} SET country_cache = ? WHERE id = ?", ('MEXICO', user_id))
            conn.commit()
            print(f"User ID {user_id} country updated to 'MEXICO'.")
        else:
            print(f"User ID {user_id} already has country '{user[3]}'.")
            
    except sqlite3.OperationalError as e:
        print(f"Error checking user: {e}")

def main():
    conn = get_db_connection()
    if not conn:
        return

    tables = check_tables(conn)
    
    # Determine proper table name (Reflex defaults class name to lowercase)
    product_table = 'products'
    if 'Products' in tables: product_table = 'Products'
    elif 'product' in tables: product_table = 'product'
    
    user_table = 'users'
    if 'Users' in tables: user_table = 'Users'
    elif 'user' in tables: user_table = 'user'

    count = check_products(conn, product_table)
    
    if count == 0:
        seed_products(conn, product_table)
        check_products(conn, product_table) # Verify
        
    check_user_country(conn, 1, user_table)
    
    conn.close()

if __name__ == '__main__':
    main()
