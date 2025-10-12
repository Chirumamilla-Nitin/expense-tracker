from flask import Flask, render_template, request, jsonify
import csv, os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

FILENAME = os.path.join(os.path.dirname(__file__), "expenses.csv")

def init_file():
    """Ensure CSV exists with headers"""
    if not os.path.exists(FILENAME):
        with open(FILENAME, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Date", "Category", "Amount"])

def read_expenses():
    """Return all expenses as a list of dicts"""
    expenses = []
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                expenses.append(row)
    return expenses

def write_expenses(expenses):
    """Overwrite CSV with updated expenses"""
    with open(FILENAME, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["ID","Date","Category","Amount"])
        writer.writeheader()
        for exp in expenses:
            writer.writerow(exp)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_expense():
    data = request.get_json()
    category = data.get('category', '').strip()
    amount = data.get('amount')

    if not category or not amount:
        return jsonify({"error":"Missing fields"}),400

    expenses = read_expenses()
    new_id = str(int(expenses[-1]['ID'])+1 if expenses else 1)
    date = datetime.now().strftime("%Y-%m-%d")
    expenses.append({"ID": new_id, "Date": date, "Category": category, "Amount": amount})
    write_expenses(expenses)
    return jsonify({"message":"Expense added successfully!"})

@app.route('/expenses')
def get_expenses():
    category_filter = request.args.get('category')
    expenses = read_expenses()
    if category_filter and category_filter != "All":
        expenses = [exp for exp in expenses if exp['Category']==category_filter]
    return jsonify(expenses)

@app.route('/delete/<id>', methods=['DELETE'])
def delete_expense(id):
    expenses = read_expenses()
    expenses = [exp for exp in expenses if exp['ID'] != id]
    write_expenses(expenses)
    return jsonify({"message":"Deleted successfully!"})

@app.route('/edit/<id>', methods=['PUT'])
def edit_expense(id):
    data = request.get_json()
    category = data.get('category', '').strip()
    amount = data.get('amount')

    expenses = read_expenses()
    for exp in expenses:
        if exp['ID'] == id:
            exp['Category'] = category
            exp['Amount'] = amount
            break
    write_expenses(expenses)
    return jsonify({"message":"Edited successfully!"})

@app.route('/chart-data')
def chart_data():
    totals = defaultdict(float)
    for exp in read_expenses():
        try:
            totals[exp["Category"]] += float(exp["Amount"])
        except:
            pass
    return jsonify(totals)

if __name__ == '__main__':
    init_file()
    app.run(debug=True, host='0.0.0.0', port=5000)
