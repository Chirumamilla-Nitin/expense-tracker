from flask import Flask, render_template, request, jsonify
import csv, os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
FILENAME = "expenses.csv"


def init_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount"])


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add", methods=["POST"])
def add_expense():
    data = request.get_json()
    category = data.get("category")
    amount = data.get("amount")
    if not category or not amount:
        return jsonify({"error": "missing fields"}), 400
    date = datetime.now().strftime("%Y-%m-%d")
    with open(FILENAME, "a", newline="") as f:
        csv.writer(f).writerow([date, category, amount])
    return jsonify({"ok": True})


@app.route("/expenses")
def expenses():
    items = []
    if os.path.exists(FILENAME):
        with open(FILENAME) as f:
            for row in csv.DictReader(f):
                items.append(row)
    return jsonify(items)


@app.route("/chart")
def chart():
    sums = defaultdict(float)
    if os.path.exists(FILENAME):
        with open(FILENAME) as f:
            for row in csv.DictReader(f):
                try:
                    sums[row["Category"]] += float(row["Amount"])
                except ValueError:
                    pass
    return jsonify(sums)


if __name__ == "__main__":
    init_file()
    app.run(debug=True)
