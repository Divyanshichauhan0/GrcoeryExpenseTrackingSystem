# app.py
# Pyright directives removed for clarity; this file is rewritten for PostgreSQL.
import os
from typing import TypedDict

from flask import Flask, render_template, request, redirect, flash
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "secret_key")


class SpendRow(TypedDict):
    name: str
    total_spent: float


def get_db_connection():
    """
    Connect to Postgres using DATABASE_URL from environment.
    Returns a psycopg2 connection whose cursors will produce dict-like rows.
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable not set")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


@app.route("/items")
def items_page():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # LEFT JOIN so items with no purchaser (NULL) still show
        cur.execute("""
            SELECT g.id, u.name , g.item_name, g.price, g.date_added
            FROM groceryitem g
            LEFT JOIN users u ON g.purchased_by = u.id
            ORDER BY g.date_added DESC
            LIMIT 20
        """)
        latest_item = cur.fetchall()
        cur.close()
        return render_template("index.html", latest_item=latest_item)
    finally:
        conn.close()


@app.route("/people")
def people_page():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users ORDER BY id")
        users = cur.fetchall()
        cur.close()
        return render_template("people.html", users=users)
    finally:
        conn.close()


@app.route("/save_people", methods=["POST"])
def save_people():
    try:
        num_people = int(request.form.get("num_people", 0))
    except ValueError:
        flash("Invalid number of people.", "error")
        return redirect("/people")

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        for i in range(1, num_people + 1):
            name = request.form.get(f"person{i}")
            if not name:
                continue
            try:
                cur.execute("INSERT INTO users (name) VALUES (%s)", (name,))
                conn.commit()
            except psycopg2.IntegrityError:
                conn.rollback()
                flash(f"Name '{name}' already exists. Please use a different name.", "error")
                cur.close()
                return redirect("/people")
        cur.close()
    finally:
        conn.close()

    flash("People added successfully!", "success")
    return redirect("/items")


@app.route("/")
def index():
    # keep simple home; user can go to /items to see list
    return render_template("home.html")


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE groceryitem SET purchased_by = NULL WHERE purchased_by = %s", (user_id,))
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cur.close()
    finally:
        conn.close()
    return redirect("/people")


@app.route("/analysis")
def analysis():
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # Total spending per user
        cur.execute("""
            SELECT u.id, u.name, COALESCE(SUM(g.price), 0) AS total_spent
            FROM users u
            LEFT JOIN groceryitem g ON g.purchased_by = u.id
            GROUP BY u.id, u.name
        """)
        spent = cur.fetchall()

        if not spent:
            cur.close()
            return "No data available yet."

        # Convert to python dicts (RealDictCursor already gives dict-like rows)
        spent = [dict(row) for row in spent]
        for row in spent:
            row["total_spent"] = float(row["total_spent"])

        total_group_spent = sum(row["total_spent"] for row in spent)
        fair_share = total_group_spent / len(spent)

        # Payments made
        cur.execute("SELECT payer_id, COALESCE(SUM(amount), 0) AS total_paid FROM payments GROUP BY payer_id")
        paid_rows = cur.fetchall()
        paid_map = {row["payer_id"]: float(row["total_paid"]) for row in paid_rows if row["payer_id"] is not None}

        # Payments received
        cur.execute("SELECT receiver_id, COALESCE(SUM(amount), 0) AS total_received FROM payments GROUP BY receiver_id")
        received_rows = cur.fetchall()
        received_map = {row["receiver_id"]: float(row["total_received"]) for row in received_rows if row["receiver_id"] is not None}

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
        # Greedy settle-up
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

        cur.close()
        return render_template(
            "analysis.html",
            spending=balances,
            transactions=transactions,
            total_group_spent=round(total_group_spent, 2),
            fair_share=round(fair_share, 2),
        )
    finally:
        conn.close()


@app.route("/add", methods=["GET", "POST"])
def add_item():
    if request.method == "GET":
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM users ORDER BY id")
            users = cur.fetchall()
            cur.close()
            return render_template("add_itm.html", users=users)
        finally:
            conn.close()
    else:
        item_name = request.form.get("item_name", "").strip()
        price_str = request.form.get("price", "0").strip()
        purchased_by_raw = request.form.get("purchased_by", None)

        # Validate and convert
        if not item_name:
            flash("Item name cannot be empty.", "error")
            return redirect("/add")

        try:
            price = float(price_str)
        except ValueError:
            flash("Invalid price.", "error")
            return redirect("/add")

        purchased_by = None
        if purchased_by_raw and purchased_by_raw != "":
            try:
                purchased_by = int(purchased_by_raw)
            except ValueError:
                purchased_by = None

        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO groceryitem (item_name, price, purchased_by, date_added)
                VALUES (%s, %s, %s, CURRENT_DATE)
            """, (item_name, price, purchased_by))
            conn.commit()
            cur.close()
        finally:
            conn.close()
        return redirect("/items")


@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if request.method == "POST":
            item_name = request.form.get("item_name", "").strip()
            price_str = request.form.get("price", "0").strip()
            purchased_by_raw = request.form.get("purchased_by", None)

            if not item_name:
                flash("Item name cannot be empty.", "error")
                return redirect(f"/edit/{item_id}")

            try:
                price = float(price_str)
            except ValueError:
                flash("Invalid price.", "error")
                return redirect(f"/edit/{item_id}")

            purchased_by = None
            if purchased_by_raw and purchased_by_raw != "":
                try:
                    purchased_by = int(purchased_by_raw)
                except ValueError:
                    purchased_by = None

            cur.execute("""
                UPDATE groceryitem
                SET item_name = %s, price = %s, purchased_by = %s
                WHERE id = %s
            """, (item_name, price, purchased_by, item_id))
            conn.commit()
            cur.close()
            return redirect("/items")

        cur.execute("SELECT id, name FROM users ORDER BY id")
        users = cur.fetchall()
        cur.execute("SELECT * FROM groceryitem WHERE id = %s", (item_id,))
        item = cur.fetchone()
        cur.close()
        return render_template("edit.html", item=item, users=users)
    finally:
        conn.close()


@app.route("/delete/<int:item_id>")
def delete_item(item_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM groceryitem WHERE id = %s", (item_id,))
        item = cur.fetchone()
        if not item:
            cur.close()
            return "Item not found."
        cur.execute("DELETE FROM groceryitem WHERE id = %s", (item_id,))
        conn.commit()
        cur.close()
        return redirect("/items")
    finally:
        conn.close()



if __name__ == "__main__":
    app.run(debug=True)
