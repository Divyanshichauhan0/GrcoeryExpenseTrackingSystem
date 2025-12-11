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