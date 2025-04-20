def add_product(name, category, stock, threshold, cost):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, stock, threshold, cost, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, category, stock, threshold, cost, datetime.now()))
    conn.commit()
    conn.close()