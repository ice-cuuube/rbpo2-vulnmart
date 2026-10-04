from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

DB_PATH = "vulnmart.db"

# CWE-798: Hard-coded Credentials
ADMIN_PASSWORD = "admin123"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            owner TEXT,
            product TEXT,
            price INTEGER
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT
        )
    """)

    connection.execute(
        "INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'alice', 'alice123')"
    )
    connection.execute(
        "INSERT OR IGNORE INTO users (id, username, password) VALUES (2, 'bob', 'bob123')"
    )

    connection.execute(
        "INSERT OR IGNORE INTO orders (id, owner, product, price) VALUES (1, 'alice', 'Laptop', 90000)"
    )
    connection.execute(
        "INSERT OR IGNORE INTO orders (id, owner, product, price) VALUES (2, 'bob', 'Monitor', 30000)"
    )

    connection.commit()
    connection.close()


@app.route("/")
def index():
    return """
    <html>
    <head>
        <title>VulnMart-Lab</title>
    </head>
    <body>
        <h1>VulnMart-Lab</h1>

        <h2>Login</h2>
        <form method="POST" action="/login">
            <input name="username" placeholder="Username">
            <input name="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>

        <h2>Review</h2>
        <form method="POST" action="/review">
            <input name="text" placeholder="Review">
            <button type="submit">Add review</button>
        </form>

        <p><a href="/reviews">View reviews</a></p>

        <p><a href="/orders/1">Order 1</a></p>
        <p><a href="/orders/2">Order 2</a></p>

        <p><a href="/admin?password=admin123">Admin panel</a></p>
    </body>
    </html>
    """


# CWE-89: SQL Injection
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # УЯЗВИМОСТЬ: пользовательский ввод напрямую попадает в SQL-запрос
    query = f"""
        SELECT id, username
        FROM users
        WHERE username = '{username}'
        AND password = '{password}'
    """

    connection = get_db()
    user = connection.execute(query).fetchone()
    connection.close()

    if user:
        return jsonify({
            "status": "success",
            "username": user["username"]
        })

    return jsonify({
        "status": "error",
        "message": "Invalid credentials"
    }), 401


# CWE-79: Stored XSS
@app.route("/review", methods=["POST"])
def add_review():
    text = request.form.get("text", "")

    connection = get_db()
    connection.execute(
        "INSERT INTO reviews (text) VALUES (?)",
        (text,)
    )
    connection.commit()
    connection.close()

    return "Review added. <a href='/reviews'>View reviews</a>"


@app.route("/reviews")
def reviews():
    connection = get_db()
    data = connection.execute(
        "SELECT id, text FROM reviews ORDER BY id DESC"
    ).fetchall()
    connection.close()

    # УЯЗВИМОСТЬ: |safe отключает обычное экранирование HTML
    template = """
    <html>
    <body>
        <h1>Reviews</h1>

        {% for review in reviews %}
            <div>
                <b>#{{ review["id"] }}</b>
                <p>{{ review["text"]|safe }}</p>
            </div>
        {% endfor %}

    </body>
    </html>
    """

    return render_template_string(template, reviews=data)


# CWE-863: Incorrect Authorization / IDOR
@app.route("/orders/<int:order_id>")
def get_order(order_id):
    connection = get_db()

    # УЯЗВИМОСТЬ: не проверяется, имеет ли пользователь право
    # просматривать конкретный заказ
    order = connection.execute(
        "SELECT id, owner, product, price FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    connection.close()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    return jsonify(dict(order))


# CWE-798: Hard-coded Credentials / weak authentication
@app.route("/admin")
def admin():
    password = request.args.get("password", "")

    if password == ADMIN_PASSWORD:
        return jsonify({
            "status": "success",
            "message": "Admin panel"
        })

    return jsonify({
        "status": "denied"
    }), 403


if __name__ == "__main__":
    init_db()
    print("VulnMart-Lab запущен на http://127.0.0.1:5055")
    app.run(host="0.0.0.0", port=5055, debug=False)
