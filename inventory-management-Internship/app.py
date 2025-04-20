from flask import Flask, render_template_string, request, redirect
import mysql.connector
from datetime import datetime, timedelta

# ✅ MySQL Config – CHANGE THESE
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'OMKar-098',
    'database': 'inventory_db'
}

app = Flask(_name_)

def get_connection():
    return mysql.connector.connect(**db_config)

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    result = cursor.fetchall()
    conn.close()
    return result

def add_product(name, category, stock, threshold, cost):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, stock, threshold, cost, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, category, stock, threshold, cost, datetime.now()))
    conn.commit()
    conn.close()

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

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    conn.close()

# ✅ REPORT & METRICS FUNCTIONS
def get_products_updated_since(days):
    since_date = datetime.now() - timedelta(days=days)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE last_updated >= %s", (since_date,))
    result = cursor.fetchall()
    conn.close()
    return result

def get_reorder_suggestions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE stock < threshold")
    result = cursor.fetchall()
    conn.close()
    return result

def get_inventory_metrics():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(stock), SUM(stock * cost) FROM products")
    total_items, total_stock, total_value = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM products WHERE stock < threshold")
    low_stock_count = cursor.fetchone()[0]

    conn.close()
    return {
        'total_items': total_items,
        'total_stock': total_stock,
        'total_value': total_value,
        'low_stock_count': low_stock_count
    }

# ✅ ROUTES
@app.route('/')
def dashboard():
    products = get_all_products()
    metrics = get_inventory_metrics()
    reorder_suggestions = get_reorder_suggestions()
    return render_template_string(DASHBOARD_HTML, products=products, metrics=metrics, reorder=reorder_suggestions)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        add_product(
            request.form['name'],
            request.form['category'],
            int(request.form['stock']),
            int(request.form['threshold']),
            float(request.form['cost'])
        )
        return redirect('/')
    return render_template_string(ADD_HTML)

@app.route('/update/<int:product_id>', methods=['GET', 'POST'])
def update(product_id):
    product = [p for p in get_all_products() if p[0] == product_id][0]
    if request.method == 'POST':
        update_product(
            product_id,
            request.form['name'],
            request.form['category'],
            int(request.form['stock']),
            int(request.form['threshold']),
            float(request.form['cost'])
        )
        return redirect('/')
    return render_template_string(UPDATE_HTML, product=product)

@app.route('/delete/<int:product_id>')
def delete(product_id):
    delete_product(product_id)
    return redirect('/')

@app.route('/report/daily')
def daily_report():
    products = get_products_updated_since(1)
    return render_template_string(REPORT_HTML, products=products, title="📅 Daily Inventory Report")

@app.route('/report/weekly')
def weekly_report():
    products = get_products_updated_since(7)
    return render_template_string(REPORT_HTML, products=products, title="🗓 Weekly Inventory Report")

# ✅ HTML TEMPLATES
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Inventory Dashboard</title>
    <style>
        .low { color: red; font-weight: bold; }
        .ok { color: green; }
    </style>
</head>
<body>
<h1>📦 Inventory Dashboard</h1>
<a href="/add">➕ Add Product</a> |
<a href="/report/daily">📅 Daily Report</a> |
<a href="/report/weekly">🗓 Weekly Report</a>
<hr>

<h2>📊 Summary Metrics</h2>
<ul>
    <li>Total Products: {{ metrics.total_items }}</li>
    <li>Total Stock: {{ metrics.total_stock }}</li>
    <li>Total Stock Value: ₹{{ "%.2f"|format(metrics.total_value or 0) }}</li>
    <li>⚠ Low Stock Items: {{ metrics.low_stock_count }}</li>
</ul>

<h2>📉 Reorder Suggestions</h2>
{% if reorder %}
<table border="1" cellpadding="5">
<tr><th>ID</th><th>Name</th><th>Stock</th><th>Threshold</th></tr>
{% for p in reorder %}
<tr><td>{{ p[0] }}</td><td>{{ p[1] }}</td><td>{{ p[3] }}</td><td>{{ p[4] }}</td></tr>
{% endfor %}
</table>
{% else %}
<p>✅ All products are above threshold levels.</p>
{% endif %}

<hr>
<h2>📋 All Products</h2>
<table border="1" cellpadding="5">
<tr>
<th>ID</th><th>Name</th><th>Category</th><th>Stock</th><th>Threshold</th><th>Status</th><th>Cost</th><th>Last Updated</th><th>Actions</th>
</tr>
{% for p in products %}
<tr>
<td>{{ p[0] }}</td>
<td>{{ p[1] }}</td>
<td>{{ p[2] }}</td>
<td>{{ p[3] }}</td>
<td>{{ p[4] }}</td>
<td>
    {% if p[3] < p[4] %}
        <span class="low">Low</span>
    {% else %}
        <span class="ok">OK</span>
    {% endif %}
</td>
<td>₹{{ p[5] }}</td>
<td>{{ p[6] }}</td>
<td>
<a href="/update/{{ p[0] }}">Edit</a> |
<a href="/delete/{{ p[0] }}" onclick="return confirm('Delete this product?')">Delete</a>
</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

ADD_HTML = """
<h2>Add Product</h2>
<form method="post">
Name: <input name="name"><br>
Category: <input name="category"><br>
Stock: <input name="stock" type="number"><br>
Threshold: <input name="threshold" type="number"><br>
Cost: <input name="cost" type="number" step="0.01"><br>
<button type="submit">Add</button>
</form>
"""

UPDATE_HTML = """
<h2>Update Product</h2>
<form method="post">
Name: <input name="name" value="{{ product[1] }}"><br>
Category: <input name="category" value="{{ product[2] }}"><br>
Stock: <input name="stock" type="number" value="{{ product[3] }}"><br>
Threshold: <input name="threshold" type="number" value="{{ product[4] }}"><br>
Cost: <input name="cost" type="number" step="0.01" value="{{ product[5] }}"><br>
<button type="submit">Update</button>
</form>
"""

REPORT_HTML = """
<h1>{{ title }}</h1>
<a href="/">🏠 Back to Dashboard</a><hr>
<table border="1" cellpadding="5">
<tr>
<th>ID</th><th>Name</th><th>Category</th><th>Stock</th><th>Threshold</th><th>Cost</th><th>Last Updated</th>
</tr>
{% for p in products %}
<tr>
<td>{{ p[0] }}</td><td>{{ p[1] }}</td><td>{{ p[2] }}</td><td>{{ p[3] }}</td><td>{{ p[4] }}</td><td>₹{{ p[5] }}</td><td>{{ p[6] }}</td>
</tr>
{% endfor %}
</table>
"""

if __name__ == '__main__':
    app.run(debug=True)