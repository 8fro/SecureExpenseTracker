# app.py
# for run command --> py -m streamlit run app.py(file name) | streamlit run app.py(file name) 

import streamlit as st
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from cryptography.fernet import Fernet
import os
import html

# -------------------------
# CONFIG - REPLACE THESE
# -------------------------
SENDER_EMAIL = "rajpho.....xx9@gmail.com"          # <- change to your Gmail (sender)
SENDER_APP_PASSWORD = "uylhuc..xxxxxxx"     # <- change to Gmail App Password (not your normal password)

DB_FILE = "expenses.db"
KEY_FILE = "secret.key"

# -------------------------
# DB & KEY Setup
# -------------------------
# create DB connection (allow cross-thread)
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# Create table with amount as BLOB (so encrypted bytes store correctly)
c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    amount BLOB,
    description TEXT
)
''')
conn.commit()

# load or create encryption key (persisted)
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

fernet = Fernet(key)

# -------------------------
# Helpers: OTP, encryption safe functions
# -------------------------
def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices("0123456789", k=length))

def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Send OTP via Gmail SMTP using SENDER_EMAIL and SENDER_APP_PASSWORD.
    Returns True on success, False otherwise.
    """
    try:
        msg = MIMEText(f"Your OTP for Secure Expense Tracker is: {otp}")
        msg['Subject'] = "SecureExpenseTracker — OTP"
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        # Use STARTTLS
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send OTP email: {e}")
        return False

def to_bytes(token):
    """
    Normalize token to bytes. Handles bytes, memoryview, bytearray, str, None.
    """
    if token is None:
        return b''
    if isinstance(token, bytes):
        return token
    if isinstance(token, memoryview):
        return token.tobytes()
    if isinstance(token, bytearray):
        return bytes(token)
    if isinstance(token, str):
        return token.encode('utf-8')
    # fallback
    return str(token).encode('utf-8')

def safe_decrypt(token):
    """
    Try to decrypt token using Fernet. If decryption fails, return readable string.
    This prevents the TypeError and avoids crashing when encountering unexpected DB values.
    """
    try:
        token_bytes = to_bytes(token)
        return fernet.decrypt(token_bytes).decode('utf-8')
    except Exception:
        # if decrypt fails, try to decode bytes to string or return str(token)
        try:
            return to_bytes(token).decode('utf-8', errors='ignore')
        except Exception:
            return str(token)

# -------------------------
# CRUD: add & fetch
# -------------------------
def add_expense(category: str, amount: float, description: str):
    # Encrypt amount as bytes and store as BLOB
    enc = fernet.encrypt(str(amount).encode())
    c.execute("INSERT INTO expenses (category, amount, description) VALUES (?, ?, ?)",
              (category, enc, description))
    conn.commit()

def fetch_expenses():
    c.execute("SELECT id, category, amount, description FROM expenses ORDER BY id DESC")
    rows = c.fetchall()
    # decrypt amounts safely
    result = []
    for rid, cat, amt, desc in rows:
        dec_amount = safe_decrypt(amt)
        result.append((rid, cat, dec_amount, desc))
    return result

# -------------------------
# Page states in session
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = 1  # 1 = OTP, 2 = Add, 3 = DOB/View
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False
if "show_check_data" not in st.session_state:
    st.session_state.show_check_data = False
if "dob_verified" not in st.session_state:
    st.session_state.dob_verified = False

# -------------------------
# Premium CSS + small JS
# -------------------------
st.set_page_config(page_title="Secure Expense Tracker", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg-1: #0b1221;
  --card: rgba(255,255,255,0.04);
  --accent: #00e0ff;
}
body { background: linear-gradient(180deg,var(--bg-1), #0f1b2e); font-family: 'Poppins', sans-serif; }
.stApp { color: #e6f3fb; }
.header { text-align:center; padding:16px 8px; }
.h1 { color: var(--accent); font-weight:700; font-size:28px; }
.subtitle { color:#9fc7d8; margin-top:4px; font-size:13px; }
.card { background: var(--card); padding:18px; border-radius:12px; box-shadow: 0 8px 30px rgba(2,6,23,0.6); }
.row { display:flex; gap:10px; align-items:center; }
.stButton>button { background: linear-gradient(90deg,#00e0ff,#0077ff); color:white; border-radius:10px; padding:8px 14px; font-weight:600; }
input[type="text"], textarea, input[type="password"], .stNumberInput>div>input {
  background: rgba(255,255,255,0.03);
  color: #e6f3fb;
  border: 1px solid rgba(255,255,255,0.06);
  padding:8px 10px; border-radius:8px;
}
.table-wrap { background: rgba(255,255,255,0.02); border-radius:10px; padding:12px; }
thead th { color: var(--accent); }
tbody tr:hover { background: rgba(0,224,255,0.04); }
.small-muted { color:#9fb6c6; font-size:13px; }
.fade { animation: fadeIn 0.5s ease both; }
@keyframes fadeIn { from {opacity:0; transform: translateY(8px);} to {opacity:1; transform:none;} }
</style>
<script>
/* small JS to focus first input on page load */
window.addEventListener('load', () => {
  const el = document.querySelector('input');
  if(el) el.focus();
});
</script>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><div class="h1">🔒 Secure Expense Tracker</div><div class="subtitle small-muted">Encrypted • Private • Simple</div></div>', unsafe_allow_html=True)

# -------------------------
# PAGE 1: OTP (email + OTP inputs side-by-side)
# -------------------------
if st.session_state.page == 1:
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    st.subheader("Step 1 — Login with OTP")
    col1, col2 = st.columns([1, 1])

    with col1:
        email_input = st.text_input("Enter email to receive OTP", placeholder="you@example.com")
        if st.button("Send OTP"):
            if not email_input or "@" not in email_input:
                st.error("Please enter a valid email address.")
            else:
                otp = generate_otp()
                st.session_state.generated_otp = otp
                # send OTP via SMTP
                sent = send_otp_email(email_input, otp)
                if sent:
                    st.success("OTP sent — check your email (inbox/spam).")
                else:
                    st.error("Failed to send OTP. Check SMTP settings in app.py.")

    with col2:
        entered_otp = st.text_input("Enter received OTP")
        if st.button("Verify OTP"):
            if entered_otp and st.session_state.generated_otp and entered_otp == st.session_state.generated_otp:
                st.session_state.otp_verified = True
                st.session_state.page = 2
                st.success("OTP Verified — moving to Add Expense.")
                st.rerun()

            else:
                st.error("Invalid OTP.")

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# PAGE 2: Add Expense
# -------------------------
elif st.session_state.page == 2 and st.session_state.otp_verified:
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    st.subheader("Step 2 — Add New Expense")

    # Use two-column layout for nicer spacing
    left, right = st.columns([2, 1])
    with left:
        category = st.text_input("Category", placeholder="Food, Travel, Bills ...")
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
        description = st.text_area("Description (optional)", height=90)
    with right:
        if st.button("Add Expense"):
            if not category or amount <= 0:
                st.error("Please provide a category and amount > 0.")
            else:
                add_expense(category.strip(), float(amount), description.strip())
                st.success("Expense added and encrypted.")
                st.session_state.show_check_data = True

    if st.session_state.get("show_check_data"):
        st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
        if st.button("Check Your Data — View (next)"):
            st.session_state.page = 3
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# PAGE 3: DOB verification & View
# -------------------------
elif st.session_state.page == 3:
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    st.subheader("Step 3 — Verify DOB to Decrypt & View Data")

    dob_input = st.text_input("Enter DOB (dd-mm-yyyy)", type="password", placeholder="dd-mm-yyyy")
    if st.button("Verify DOB & Show Expenses"):
        if dob_input and dob_input.strip():
            st.session_state.dob_verified = True
        else:
            st.error("Please enter DOB to unlock.")

    if st.session_state.dob_verified:
        expenses = fetch_expenses()
        if not expenses:
            st.info("No expenses recorded yet.")
        else:
            # Build stylized HTML table to keep premium look
            table_html = "<div class='table-wrap'><table style='width:100%; border-collapse:collapse;'><thead><tr><th style='text-align:left;padding:8px;'>ID</th><th style='text-align:left;padding:8px;'>Category</th><th style='text-align:left;padding:8px;'>Amount (₹)</th><th style='text-align:left;padding:8px;'>Description</th></tr></thead><tbody>"
            for rid, cat, amt, desc in expenses:
                cat_escaped = html.escape(str(cat))
                desc_escaped = html.escape(str(desc))
                amt_escaped = html.escape(str(amt))
                table_html += f"<tr><td style='padding:8px;border-top:1px solid rgba(255,255,255,0.03);'>{rid}</td><td style='padding:8px;border-top:1px solid rgba(255,255,255,0.03);'>{cat_escaped}</td><td style='padding:8px;border-top:1px solid rgba(255,255,255,0.03);'>{amt_escaped}</td><td style='padding:8px;border-top:1px solid rgba(255,255,255,0.03);'>{desc_escaped}</td></tr>"
            table_html += "</tbody></table></div>"
            st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Footer / tips
st.markdown("<hr style='opacity:0.06'/>", unsafe_allow_html=True)
st.markdown("<div class='small-muted' style='text-align:center'>Keep <code>secret.key</code> safe. If lost, previously encrypted amounts cannot be recovered.</div>", unsafe_allow_html=True)



####################################################################################################################################################################################################
# Here is no any OTP genreter bacause this is for testing code time and again an again otp check


# app.py
import streamlit as st
import sqlite3
import random
import string
import os
from cryptography.fernet import Fernet
# smtplib and email are left below if you want to enable real email sending
import smtplib
from email.mime.text import MIMEText

# -----------------------------
# CONFIG
# -----------------------------
DEV_MODE = True   # True = show OTP in app (development). False = send real email via SMTP.
SENDER_EMAIL = "youremail@gmail.com"         # only required if DEV_MODE=False
SENDER_APP_PASSWORD = "your_app_password"    # only required if DEV_MODE=False (Gmail app password)
# Note: do not commit real credentials to GitHub. Use environment variables for production.

DB_FILE = "expenses.db"
KEY_FILE = "secret.key"

# -----------------------------
# DB + KEY Setup
# -----------------------------
# ensure DB exists and table exists
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        amount TEXT,
        description TEXT
    )
''')
conn.commit()

# load or create encryption key (persisted to KEY_FILE)
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

fernet = Fernet(key)

# -----------------------------
# Helpers: OTP, send, safe decrypt
# -----------------------------
def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def send_otp_via_smtp(to_email: str, otp: str) -> bool:
    """
    Send OTP via Gmail SMTP. Only used when DEV_MODE=False.
    Requires SENDER_EMAIL and SENDER_APP_PASSWORD to be set correctly.
    """
    try:
        msg = MIMEText(f"Your OTP for Secure Expense Tracker is: {otp}")
        msg["Subject"] = "SecureExpenseTracker — OTP"
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send OTP: {e}")
        return False

def to_bytes(token):
    """Normalize token to bytes so Fernet.decrypt accepts it.
       Handles bytes, memoryview, bytearray, str and None."""
    if token is None:
        return b''
    if isinstance(token, bytes):
        return token
    if isinstance(token, memoryview):
        return token.tobytes()
    if isinstance(token, bytearray):
        return bytes(token)
    if isinstance(token, str):
        # token may be a decoded string - convert to bytes
        return token.encode('utf-8')
    # fallback
    return str(token).encode('utf-8')

def safe_decrypt(token):
    """Try to decrypt token; if any error, return readable string (won't crash UI)."""
    try:
        token_bytes = to_bytes(token)
        return fernet.decrypt(token_bytes).decode('utf-8')
    except Exception:
        # If decrypt fails, try to present token as readable string
        try:
            return to_bytes(token).decode('utf-8', errors='ignore')
        except Exception:
            return str(token)

# -----------------------------
# CRUD operations (use text for stored encrypted token)
# -----------------------------
def add_expense(category: str, amount: float, description: str):
    # store encrypted amount as UTF-8 string (avoids memoryview/BLOB issues)
    encrypted_amount = fernet.encrypt(str(amount).encode()).decode('utf-8')
    c.execute("INSERT INTO expenses (category, amount, description) VALUES (?, ?, ?)",
              (category, encrypted_amount, description))
    conn.commit()

def get_all_expenses():
    c.execute("SELECT id, category, amount, description FROM expenses ORDER BY id DESC")
    rows = c.fetchall()
    # decrypt amount for display using safe_decrypt
    return [(rid, cat, safe_decrypt(amount), desc) for (rid, cat, amount, desc) in rows]

# -----------------------------
# Premium UI (CSS + font + small JS snippet)
# -----------------------------
st.set_page_config(page_title="Secure Expense Tracker", layout="wide")
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg1: #0f1724;
  --bg2: #111827;
  --accent: #00e0ff;
  --card: rgba(255,255,255,0.04);
}
body { background: linear-gradient(180deg, var(--bg1), var(--bg2)); font-family: 'Poppins', sans-serif; }
.stApp { color: #e6eef6; }
.header {
  text-align:center;
  padding: 18px 10px;
  margin-bottom: 8px;
}
.card {
  background: var(--card);
  border-radius: 14px;
  padding: 18px;
  box-shadow: 0 8px 30px rgba(2,6,23,0.6);
  backdrop-filter: blur(6px);
}
.title {
  font-size: 28px;
  color: var(--accent);
  font-weight:700;
}
.subtitle { color: #bcd7e6; margin-top:6px; margin-bottom:0; }
.sidebar .sidebar-content { background: rgba(0,0,0,0.35); }
.stButton>button {
  background: linear-gradient(90deg,#00e0ff,#0077ff);
  color: white; border: none; padding: 8px 14px; border-radius: 10px; font-weight:600;
}
.stButton>button:hover { transform: translateY(-2px); box-shadow:0 8px 30px rgba(0,224,255,0.12); }
input[type="text"], textarea, input[type="password"], .stNumberInput>div>input {
  background: rgba(255,255,255,0.03);
  color: #e6eef6;
  border: 1px solid rgba(255,255,255,0.06);
  padding: 8px 10px; border-radius:8px;
}
.table-wrap { background: rgba(255,255,255,0.02); border-radius:10px; padding: 10px; }
thead th { color: var(--accent); }
tbody tr:hover { background: rgba(0,224,255,0.06); }
.small-muted { color: #9fb6c6; font-size:13px; }
.fade { animation: fadeIn .6s ease both; }
@keyframes fadeIn { from {opacity:0; transform: translateY(6px);} to {opacity:1; transform:none;} }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><div class="title">🔒 Secure Expense Tracker</div><div class="subtitle small-muted">Private • Encrypted • Simple</div></div>', unsafe_allow_html=True)

# -----------------------------
# App Flow (OTP -> Main -> DOB unlock for viewing)
# -----------------------------
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False
if "dob_verified" not in st.session_state:
    st.session_state.dob_verified = False

# OTP Section (unchanged in flow; dev mode prints OTP)
if not st.session_state.otp_verified:
    with st.container():
        st.markdown('<div class="card fade">', unsafe_allow_html=True)
        st.subheader("Step 1 — Login with OTP")
        user_email = st.text_input("Enter your email to receive OTP")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Send OTP"):
                if not user_email:
                    st.error("Please enter an email first.")
                else:
                    otp = generate_otp()
                    st.session_state.generated_otp = otp
                    if DEV_MODE:
                        # developer-friendly: show OTP in-app (do not use in production)
                        st.info(f"Dev OTP: {otp}")
                        st.success("OTP generated (dev mode).")
                    else:
                        sent = send_otp_via_smtp(user_email, otp)
                        if sent:
                            st.success("OTP sent to your email.")
                        # send_otp_via_smtp already shows errors via st.error if fail
        with col2:
            entered = st.text_input("Enter OTP received")
            if st.button("Verify OTP"):
                if entered and entered == st.session_state.get("generated_otp"):
                    st.session_state.otp_verified = True
                    st.success("OTP Verified ✅ — You can use the app.")
                else:
                    st.error("Invalid OTP.")

        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()  # stop further rendering until OTP verified

# Main app area (post OTP)
left, right = st.columns([2, 3])

with left:
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    st.subheader("Add Expense")
    cat = st.text_input("Category", placeholder="e.g. Food, Travel")
    amt = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    desc = st.text_area("Description (optional)", height=80)
    if st.button("Add Expense"):
        if not cat or amt <= 0:
            st.error("Please provide a category and an amount > 0.")
        else:
            add_expense(cat.strip(), float(amt), desc.strip())
            st.success("Expense added and encrypted ✅")
    st.markdown('<p class="small-muted">Your amounts are encrypted locally (secret.key stored in app folder)</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card fade">', unsafe_allow_html=True)
    st.subheader("View Expenses (DOB unlock)")
    st.markdown('<p class="small-muted">To decrypt and view expenses, enter your DOB (any non-empty value is accepted in this demo)</p>', unsafe_allow_html=True)
    dob = st.text_input("Enter DOB (dd-mm-yyyy)", type="password")
    if st.button("Unlock & Show Expenses"):
        if dob and dob.strip():
            st.session_state.dob_verified = True
        else:
            st.error("Please enter DOB to unlock.")

    if st.session_state.dob_verified:
        expenses = get_all_expenses()
        if not expenses:
            st.info("No expenses yet.")
        else:
            # build a table with id, category, amount, description
            st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
            # create simple HTML table to preserve styles
            table_html = "<table><thead><tr><th>ID</th><th>Category</th><th>Amount (₹)</th><th>Description</th></tr></thead><tbody>"
            for rid, cat, amount, desc in expenses:
                # escape HTML in text roughly
                cat_s = str(cat).replace("<","&lt;").replace(">","&gt;")
                desc_s = str(desc).replace("<","&lt;").replace(">","&gt;")
                table_html += f"<tr><td>{rid}</td><td>{cat_s}</td><td>{amount}</td><td>{desc_s}</td></tr>"
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr style='opacity:0.08'/>", unsafe_allow_html=True)
st.markdown("<div class='small-muted' style='text-align:center'>Tip: Keep <code>secret.key</code> safe — if deleted, old encrypted data cannot be recovered.</div>", unsafe_allow_html=True)


###############################################################################################################################################################################################################################################
