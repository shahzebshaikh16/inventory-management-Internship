def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()
    conn.close()
    return result