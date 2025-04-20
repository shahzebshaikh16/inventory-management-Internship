def update_product(product_id, name, category, stock, threshold, cost):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products
        SET name=%s, category=%s, stock=%s, threshold=%s, cost=%s, last_updated=%s
        WHERE id=%s
    """, (name, category, stock, threshold, cost, datetime.now(), product_id))
    conn.commit()
    conn.close()