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


#################################################################################################################################################################################################################

import streamlit as st
import sqlite3
import smtplib
import random
import string
from cryptography.fernet import Fernet
import os

# ---------------- Database Setup ----------------
conn = sqlite3.connect("expenses.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, amount TEXT, description TEXT)''')
conn.commit()

# ---------------- Encryption Key Setup ----------------
KEY_FILE = "secret.key"
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
else:
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()

fernet = Fernet(key)

# ---------------- OTP System ----------------
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp(email, otp):
    sender_email = "ra....xx9@gmail.com"  # Change this
    sender_password = "app password"  # App password from Gmail settings

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        message = f"Subject: Your OTP Code\n\nYour OTP is {otp}"
        server.sendmail(sender_email, email, message)

# ---------------- App Pages ----------------
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

if "dob_verified" not in st.session_state:
    st.session_state.dob_verified = False

st.title("🔒 Secure Expense Tracker")

if not st.session_state.otp_verified:
    st.subheader("Login with OTP")
    email = st.text_input("Enter your email")
    if st.button("Send OTP"):
        if email:
            otp = generate_otp()
            st.session_state.generated_otp = otp
            send_otp(email, otp)
            st.success("OTP sent! Check your email.")
        else:
            st.error("Please enter your email.")

    entered_otp = st.text_input("Enter OTP")
    if st.button("Verify OTP"):
        if entered_otp == st.session_state.get("generated_otp"):
            st.session_state.otp_verified = True
            st.success("OTP Verified! You can now use the app.")
        else:
            st.error("Invalid OTP")
else:
    menu = ["Add Expense", "View Expenses"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Expense":
        st.subheader("Add New Expense")
        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0.0)
        description = st.text_area("Description")
        if st.button("Add"):
            encrypted_amount = fernet.encrypt(str(amount).encode())
            c.execute("INSERT INTO expenses (category, amount, description) VALUES (?, ?, ?)",
                      (category, encrypted_amount, description))
            conn.commit()
            st.success("Expense added successfully with encryption!")

    elif choice == "View Expenses":
        if not st.session_state.dob_verified:
            dob = st.text_input("Enter DOB (dd-mm-yyyy)")
            if st.button("Verify DOB"):
                if dob == "01-01-2000":  # Change this to your actual DOB
                    st.session_state.dob_verified = True
                    st.success("DOB Verified!") #01-01-2000
                else:
                    st.error("Incorrect DOB!")
        else:
            c.execute("SELECT category, amount, description FROM expenses")
            data = c.fetchall()
            decrypted_data = [(cat, fernet.decrypt(amount).decode(), desc) for cat, amount, desc in data]
            st.table(decrypted_data)

