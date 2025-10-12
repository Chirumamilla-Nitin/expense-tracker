from flask import Flask, render_template, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

# CSV file path
FILENAME = "expenses.csv"



def init_file():
    """Create CSV file if it doesn't exist, with headers"""
    if not os.path.exists(FILENAME):
        with open(FILENAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Date", "Category", "Amount"])

def read_expenses():
    """Read all expenses and return as a list of dicts"""
    expenses = []
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                expenses.append(row)
    return expenses

def write_expenses(expenses):
    """Overwrite CSV with updated expenses"""
    with open(FILENAME, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Date", "Category", "Amount"])
        writer.writeheader()
        for exp in expenses:
            writer.writerow(exp)



@app.route("/")
def home():
    """Render the main page"""
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add_expense():
    """Add a new expense"""
    data = request.get_json()
    category = data.get("category", "").strip()
    amount = data.get("amount")

    if not category or not amount:
        return jsonify({"error": "Missing fields"}), 400

    expenses = read_expenses()
    # Generate new ID
    new_id = str(int(expenses[-1]["ID"]) + 1 if expenses else 1)
    date = datetime.now().strftime("%Y-%m-%d")

    expenses.append({"ID": new_id, "Date": date, "Category": category, "Amount": amount})
    write_expenses(expenses)

    return jsonify({"message": "Expense added!"})

@app.route("/expenses")
def get_expenses():
    """Return all expenses or filtered by category"""
    category_filter = request.args.get("category")
    expenses = read_expenses()
    if category_filter and category_filter != "All":
        expenses = [exp for exp in expenses if exp["Category"] == category_filter]
    return jsonify(expenses)

@app.route("/delete/<id>", methods=["DELETE"])
def delete_expense(id):
    """Delete an expense by ID"""
    expenses = read_expenses()
    expenses = [exp for exp in expenses if exp["ID"] != id]
    write_expenses(expenses)
    return jsonify({"message": "Deleted!"})

@app.route("/edit/<id>", methods=["PUT"])
def edit_expense(id):
    """Edit an existing expense"""
    data = request.get_json()
    category = data.get("category", "").strip()
    amount = data.get("amount")

    expenses = read_expenses()
    for exp in expenses:
        if exp["ID"] == id:
            exp["Category"] = category
            exp["Amount"] = amount
            break
    write_expenses(expenses)
    return jsonify({"message": "Edited!"})

@app.route("/chart-data")
def chart_data():
    """Return category-wise totals for pie chart"""
    expenses = read_expenses()
    totals = {}
    for exp in expenses:
        cat = exp["Category"]
        amt = float(exp["Amount"])
        totals[cat] = totals.get(cat, 0) + amt
    return jsonify(totals)

# Run App 
if __name__ == "__main__":
    init_file()
    app.run(debug=True, host="0.0.0.0", port=5000)
