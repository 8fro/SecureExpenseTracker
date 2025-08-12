import streamlit as st
import sqlite3
from datetime import date

# ---------------- Functions ----------------
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
    ''')
    conn.commit()
    conn.close()

def add_expense(expense_date, category, amount, description):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
              (expense_date, category, amount, description))
    conn.commit()
    conn.close()

def get_expenses():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT date, category, amount, description FROM expenses ORDER BY date DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ---------------- Main App ----------------
init_db()

st.title("💰 Secure Expense Tracker - Add Expense")

with st.form("expense_form", clear_on_submit=True):
    expense_date = st.date_input("Date", date.today())
    category = st.text_input("Category", placeholder="e.g. Food, Travel, Bills")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    description = st.text_area("Description", placeholder="Enter details...")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if category and amount > 0:
            add_expense(expense_date.strftime("%Y-%m-%d"), category, amount, description)
            st.success("✅ Expense added successfully!")
        else:
            st.error("⚠ Please fill all required fields (Category & Amount).")

# ---------------- View Expenses ----------------
st.subheader("📊 Expense Records")

rows = get_expenses()
if rows:
    st.table(rows)
else:
    st.info("No expenses recorded yet.")
