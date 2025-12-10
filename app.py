# pyright: reportGeneralTypeIssues=false
# pyright: reportOptionalSubscript=false
import sqlite3
from flask import Flask, render_template, request, redirect, flash
from typing import TypedDict

app = Flask(__name__)
app.secret_key = "secret_key"


class SpendRow(TypedDict):
    name: str
    total_spent: float


def get_db_connection():
    conn = sqlite3.connect("grocery.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/items")
def items_page():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT g.id, u.name, g.item_name, g.price, g.date_added
        FROM groceryitem g
        JOIN users u ON g.purchased_by = u.id
        ORDER BY g.date_added DESC
        LIMIT 10
    """)

    latest_item = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("index.html", latest_item=latest_item)


@app.route("/people")
def people_page():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("people.html", users=users)


@app.route("/save_people", methods=["POST"])
def save_people():
    num_people = int(request.form["num_people"])

    conn = get_db_connection()
    cursor = conn.cursor()

    for i in range(1, num_people + 1):
        name = request.form.get(f"person{i}")

        if not name:
            continue

        try:
            cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
            conn.commit()

        except sqlite3.IntegrityError:
            flash(f"Name '{name}' already exists. Please use a different name.", "error")
            cursor.close()
            conn.close()
            return redirect("/people")

    cursor.close()
    conn.close()

    flash("People added successfully!", "success")
    return redirect("/items")


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE groceryitem SET purchased_by = NULL WHERE purchased_by = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/people")


@app.route("/analysis")
def analysis():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total spending per user
    cursor.execute("""
        SELECT u.id, u.name, COALESCE(SUM(g.price), 0) AS total_spent
        FROM users u
        LEFT JOIN groceryitem g ON g.purchased_by = u.id
        GROUP BY u.id, u.name
    """)

    spent = cursor.fetchall()

    if not spent:
        return "No data available yet."

    # Convert to float
    spent = [dict(row) for row in spent]
    for row in spent:
        row["total_spent"] = float(row["total_spent"])

    total_group_spent = sum(row["total_spent"] for row in spent)
    fair_share = total_group_spent / len(spent)

    # Payments made
    cursor.execute("SELECT payer_id, COALESCE(SUM(amount), 0) FROM payments GROUP BY payer_id")
    paid_rows = cursor.fetchall()
    paid_map = {row[0]: float(row[1]) for row in paid_rows}

    # Payments received
    cursor.execute("SELECT receiver_id, COALESCE(SUM(amount), 0) FROM payments GROUP BY receiver_id")
    received_rows = cursor.fetchall()
    received_map = {row[0]: float(row[1]) for row in received_rows}

    balances = []
    for row in spent:
        uid = row["id"]
        total_spent = row["total_spent"]
        paid = paid_map.get(uid, 0)
        received = received_map.get(uid, 0)

        balance = total_spent - fair_share - paid + received

        balances.append({
            "id": uid,
            "name": row["name"],
            "total_spent": total_spent,
            "paid": paid,
            "received": received,
            "balance": round(balance, 2),
        })

    payers = [b for b in balances if b["balance"] < 0]
    receivers = [b for b in balances if b["balance"] > 0]

    transactions = []

    for r in receivers:
        for p in payers:
            if p["balance"] == 0:
                continue

            amount = min(r["balance"], abs(p["balance"]))

            if amount > 0:
                transactions.append({
                    "from": p["name"],
                    "to": r["name"],
                    "from_id": p["id"],
                    "to_id": r["id"],
                    "amount": round(amount, 2),
                })

                r["balance"] -= amount
                p["balance"] += amount

    cursor.close()
    conn.close()

    return render_template(
        "analysis.html",
        spending=balances,
        transactions=transactions,
        total_group_spent=round(total_group_spent, 2),
        fair_share=round(fair_share, 2),
    )


@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "GET":
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM users")
        users = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("add_itm.html", users=users)

    else:
        conn = get_db_connection()
        cursor = conn.cursor()

        item_name = request.form["item_name"]
        price = request.form["price"]
        purchased_by = request.form["purchased_by"]

        cursor.execute("""
            INSERT INTO groceryitem (item_name, price, purchased_by, date_added)
            VALUES (?, ?, ?, DATE('now'))
        """, (item_name, price, purchased_by))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/items")


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        item_name = request.form["item_name"]
        price = request.form["price"]
        purchased_by = request.form["purchased_by"]

        cursor.execute("""
            UPDATE groceryitem
            SET item_name = ?, price = ?, purchased_by = ?
            WHERE id = ?
        """, (item_name, price, purchased_by, item_id))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/items")

    cursor.execute("SELECT id, name FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM groceryitem WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit.html", item=item, users=users)


@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM groceryitem WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    if not item:
        cursor.close()
        conn.close()
        return "Item not found."

    cursor.execute("DELETE FROM groceryitem WHERE id = ?", (item_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/items")


@app.route("/testdb")
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        cursor.close()
        conn.close()

        return f"Connected to SQLite. Tables: {tables}"

    except Exception as e:
        return f"Connection failed: {e}"


if __name__ == "__main__":
    app.run(debug=True)
