"""Secure Expense Tracker — Cyber UI

Run: streamlit run app.py
"""

import os
import html
import random
import sqlite3
import smtplib
from email.mime.text import MIMEText

import streamlit as st
from cryptography.fernet import Fernet


# -----------------------------
# CONFIG
# -----------------------------
DEV_MODE = False  # True = show OTP in-app; False = use SMTP
SENDER_EMAIL = os.getenv("SET_SENDER_EMAIL", "rajphoto1819@gmail.com")
SENDER_APP_PASSWORD = os.getenv("SET_SENDER_APP_PASSWORD", "uylhuckjfcwkxhez")

DB_FILE = "expenses.db"
KEY_FILE = "secret.key"


# -----------------------------
# DB + KEY Setup
# -----------------------------
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute(
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        amount TEXT,
        description TEXT
    )
    """
)
conn.commit()

if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()

fernet = Fernet(key)


# -----------------------------
# Helpers
# -----------------------------
def generate_otp(length: int = 6) -> str:
    return "".join(random.choices("0123456789", k=length))


def send_otp_via_smtp(to_email: str, otp: str) -> bool:
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
    if token is None:
        return b""
    if isinstance(token, bytes):
        return token
    if isinstance(token, memoryview):
        return token.tobytes()
    if isinstance(token, bytearray):
        return bytes(token)
    if isinstance(token, str):
        return token.encode("utf-8")
    return str(token).encode("utf-8")


def safe_decrypt(token):
    try:
        token_bytes = to_bytes(token)
        return fernet.decrypt(token_bytes).decode("utf-8")
    except Exception:
        try:
            return to_bytes(token).decode("utf-8", errors="ignore")
        except Exception:
            return str(token)


def add_expense(category: str, amount: float, description: str):
    encrypted_amount = fernet.encrypt(str(amount).encode()).decode("utf-8")
    c.execute(
        "INSERT INTO expenses (category, amount, description) VALUES (?, ?, ?)",
        (category, encrypted_amount, description),
    )
    conn.commit()


def fetch_expenses():
    c.execute("SELECT id, category, amount, description FROM expenses ORDER BY id DESC")
    rows = c.fetchall()
    return [(rid, cat, safe_decrypt(amount), desc) for (rid, cat, amount, desc) in rows]


def compute_stats(rows):
    total_count = len(rows)
    total_amount = 0.0
    categories = set()
    for _, cat, amt, _ in rows:
        categories.add(str(cat).strip())
        try:
            total_amount += float(str(amt))
        except Exception:
            pass
    return total_count, total_amount, len([c for c in categories if c])


# -----------------------------
# Ultra Modern Cyber UI
# -----------------------------
st.set_page_config(page_title="Secure Expense Tracker", page_icon="🛡️", layout="wide")

# Advanced CSS with stunning effects
st.markdown(
    """
<style>
/* Ultra Modern Cyber Theme */
:root {
    --primary: #00d4ff;
    --secondary: #00ff88;
    --accent: #ff6b35;
    --danger: #ff2e63;
    --success: #00ff88;
    --warning: #ff6b35;
    --dark-bg: #0a0f1a;
    --card-bg: rgba(255,255,255,0.03);
    --border: rgba(255,255,255,0.08);
    --glow: rgba(0,212,255,0.3);
    --neon-glow: 0 0 20px rgba(0,212,255,0.6), 0 0 40px rgba(0,212,255,0.3);
}

/* Advanced Animations */
@keyframes matrix {
    0% { transform: translateY(-100vh) rotate(0deg); opacity: 0; }
    50% { opacity: 0.8; }
    100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
}

@keyframes glitch {
    0% { transform: translate(0); filter: hue-rotate(0deg); }
    20% { transform: translate(-2px, 2px); filter: hue-rotate(90deg); }
    40% { transform: translate(-2px, -2px); filter: hue-rotate(180deg); }
    60% { transform: translate(2px, 2px); filter: hue-rotate(270deg); }
    80% { transform: translate(2px, -2px); filter: hue-rotate(360deg); }
    100% { transform: translate(0); filter: hue-rotate(0deg); }
}

@keyframes scanline {
    0% { transform: translateY(-100%); opacity: 0; }
    50% { opacity: 1; }
    100% { transform: translateY(100vh); opacity: 0; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(50px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-100px) skewX(-10deg);
    }
    to {
        opacity: 1;
        transform: translateX(0) skewX(0deg);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(100px) skewX(10deg);
    }
    to {
        opacity: 1;
        transform: translateX(0) skewX(0deg);
    }
}

@keyframes typewriter {
    from { width: 0; }
    to { width: 100%; }
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(180deg); }
}

@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Ultra Background */
.main .block-container {
    background: 
        radial-gradient(2000px 1000px at 10% -5%, rgba(0,212,255,0.15), transparent),
        radial-gradient(1500px 800px at 90% 10%, rgba(0,255,136,0.12), transparent),
        radial-gradient(1200px 600px at 50% 90%, rgba(255,46,99,0.08), transparent),
        linear-gradient(135deg, #0a0f1a 0%, #1a1f2a 50%, #0a0f1a 100%);
    color: #ffffff;
    position: relative;
    overflow: hidden;
    min-height: 100vh;
}

/* Matrix Rain Effect */
.main .block-container::before {
    content: "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: rgba(0, 212, 255, 0.1);
    line-height: 12px;
    white-space: pre-wrap;
    pointer-events: none;
    z-index: -1;
    animation: matrix 25s linear infinite;
}

/* Scanline Effect */
.main .block-container::after {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--primary), var(--secondary), transparent);
    animation: scanline 4s linear infinite;
    pointer-events: none;
    z-index: 1;
    box-shadow: 0 0 20px var(--primary);
}

/* Ultra Header */
.header {
    text-align: center;
    padding: 3rem 2rem;
    margin-bottom: 3rem;
    background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(0,255,136,0.1));
    border-radius: 25px;
    border: 2px solid var(--border);
    position: relative;
    overflow: hidden;
    animation: fadeInUp 2s ease-out;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.header::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.2), transparent);
    animation: slideInLeft 3s ease-out 1s forwards;
}

.header::after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), var(--secondary), transparent);
    animation: gradientShift 3s ease infinite;
}

.brand {
    font-size: 3.5rem;
    font-weight: 900;
    color: var(--primary);
    text-shadow: var(--neon-glow);
    margin-bottom: 1rem;
    animation: glitch 0.3s ease-in-out infinite;
    position: relative;
    letter-spacing: 3px;
}

.brand::before {
    content: "🛡️";
    position: absolute;
    left: -60px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 2.5rem;
    animation: float 3s ease-in-out infinite;
}

.brand::after {
    content: "🛡️";
    position: absolute;
    right: -60px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 2.5rem;
    animation: float 3s ease-in-out infinite 1.5s;
}

.sub {
    color: #cccccc;
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Ultra Cards */
.card {
    background: var(--card-bg);
    padding: 2rem;
    border-radius: 20px;
    border: 2px solid var(--border);
    margin-bottom: 2rem;
    backdrop-filter: blur(20px);
    animation: fadeInUp 1.5s ease-out;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    box-shadow: 0 15px 45px rgba(0,0,0,0.3);
}

.card::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.1), transparent);
    transition: left 0.8s ease;
}

.card:hover::before {
    left: 100%;
}

.card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 25px 70px rgba(0,212,255,0.2);
    border-color: var(--primary);
}

/* Ultra Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), var(--secondary), var(--primary));
    background-size: 200% 200%;
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 15px;
    font-weight: 800;
    font-size: 1rem;
    letter-spacing: 1px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    animation: gradientShift 3s ease infinite;
    box-shadow: 0 8px 25px rgba(0,212,255,0.4);
    text-transform: uppercase;
}

.stButton > button::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.6s ease;
}

.stButton > button:hover::before {
    left: 100%;
}

.stButton > button:hover {
    transform: translateY(-5px) scale(1.05);
    box-shadow: 0 15px 40px rgba(0,212,255,0.6);
    animation: glitch 0.3s ease-in-out;
}

/* Ultra Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05);
    color: white;
    border: 2px solid var(--border);
    border-radius: 15px;
    padding: 1rem;
    font-size: 1rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--primary);
    box-shadow: 0 0 20px rgba(0,212,255,0.3);
    background: rgba(255,255,255,0.08);
    transform: translateY(-2px);
}

/* Ultra Stepper */
.stepper {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin: 3rem 0 2rem;
    flex-wrap: wrap;
    animation: fadeInUp 1.5s ease-out 0.5s both;
}

.step {
    padding: 1rem 2rem;
    border-radius: 15px;
    border: 2px solid var(--border);
    background: var(--card-bg);
    color: #cccccc;
    font-weight: 700;
    font-size: 1rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
    letter-spacing: 1px;
}

.step::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.2), transparent);
    transition: left 0.6s ease;
}

.step:hover::before {
    left: 100%;
}

.step.active {
    border-color: var(--primary);
    background: rgba(0,212,255,0.1);
    color: var(--primary);
    box-shadow: 0 0 30px rgba(0,212,255,0.4);
    animation: pulse 2s ease-in-out infinite;
    transform: scale(1.1);
}

/* Ultra Stats */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.stat-card {
    background: var(--card-bg);
    padding: 1.5rem;
    border-radius: 15px;
    border: 2px solid var(--border);
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.1), transparent);
    transition: left 0.5s ease;
}

.stat-card:hover::before {
    left: 100%;
}

.stat-card:hover {
    transform: translateY(-5px);
    border-color: var(--primary);
    box-shadow: 0 10px 30px rgba(0,212,255,0.2);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 900;
    color: var(--primary);
    text-shadow: 0 0 15px rgba(0,212,255,0.5);
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 0.9rem;
    color: #cccccc;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

/* Ultra Table */
.dataframe {
    background: var(--card-bg);
    border-radius: 15px;
    overflow: hidden;
    border: 2px solid var(--border);
    backdrop-filter: blur(10px);
}

.dataframe th {
    background: rgba(0,212,255,0.1);
    color: var(--primary);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 1rem;
}

.dataframe td {
    color: white;
    border-bottom: 1px solid var(--border);
    padding: 1rem;
    transition: all 0.3s ease;
}

.dataframe tr:hover {
    background: rgba(0,212,255,0.05);
    transform: scale(1.01);
}

/* Status Indicators */
.status {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 0.25rem;
    position: relative;
    overflow: hidden;
    animation: pulse 2s ease-in-out infinite;
}

.status::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s ease;
}

.status:hover::before {
    left: 100%;
}

.status.success {
    background: rgba(0,255,136,0.2);
    color: var(--success);
    border: 2px solid var(--success);
    box-shadow: 0 0 20px rgba(0,255,136,0.3);
}

.status.warning {
    background: rgba(255,107,53,0.2);
    color: var(--warning);
    border: 2px solid var(--warning);
    box-shadow: 0 0 20px rgba(255,107,53,0.3);
}

.status.danger {
    background: rgba(255,46,99,0.2);
    color: var(--danger);
    border: 2px solid var(--danger);
    box-shadow: 0 0 20px rgba(255,46,99,0.3);
}

/* Loading Screen */
.loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: var(--dark-bg);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    animation: fadeInUp 0.5s ease-out;
}

.loading-text {
    font-family: 'Courier New', monospace;
    color: var(--primary);
    font-size: 2rem;
    font-weight: 700;
    animation: blink 1s infinite;
    text-shadow: 0 0 20px var(--primary);
    letter-spacing: 3px;
}

/* Matrix Characters */
.matrix-char {
    position: absolute;
    color: var(--primary);
    font-family: 'Courier New', monospace;
    font-size: 14px;
    opacity: 0.8;
    animation: matrix 4s linear infinite;
    text-shadow: 0 0 10px var(--primary);
}

/* Responsive Design */
@media (max-width: 768px) {
    .brand { font-size: 2.5rem; }
    .brand::before, .brand::after { display: none; }
    .stepper { flex-direction: column; align-items: center; }
    .stats-grid { grid-template-columns: 1fr; }
    .card { padding: 1.5rem; }
    .header { padding: 2rem 1rem; }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.02);
    border-radius: 6px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--primary), var(--secondary));
    border-radius: 6px;
    box-shadow: 0 0 15px rgba(0,212,255,0.5);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #00f0ff, #00ffb3);
    box-shadow: 0 0 20px rgba(0,212,255,0.8);
}
</style>

<script>
// Enhanced Matrix Rain Effect
function createMatrixRain() {
    const chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン";
    const container = document.querySelector('.main .block-container');
    
    for (let i = 0; i < 80; i++) {
        const char = document.createElement('div');
        char.className = 'matrix-char';
        char.textContent = chars[Math.floor(Math.random() * chars.length)];
        char.style.left = Math.random() * 100 + '%';
        char.style.animationDelay = Math.random() * 4 + 's';
        char.style.animationDuration = (Math.random() * 3 + 3) + 's';
        char.style.fontSize = (Math.random() * 8 + 10) + 'px';
        container.appendChild(char);
    }
}

// Advanced Typewriter Effect
function typewriterEffect() {
    const brand = document.querySelector('.brand');
    if (brand) {
        const text = brand.textContent;
        brand.textContent = '';
        let i = 0;
        
        function type() {
            if (i < text.length) {
                brand.textContent += text.charAt(i);
                i++;
                setTimeout(type, 80);
            }
        }
        type();
    }
}

// Glitch Effect on Hover
function addGlitchEffect() {
    const elements = document.querySelectorAll('.card, .step, .stButton button, .stat-card');
    elements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.animation = 'glitch 0.3s ease-in-out';
        });
        element.addEventListener('mouseleave', function() {
            this.style.animation = '';
        });
    });
}

// Particle System
function createParticles() {
    const container = document.querySelector('.main .block-container');
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'absolute';
        particle.style.width = '3px';
        particle.style.height = '3px';
        particle.style.background = `hsl(${Math.random() * 60 + 180}, 100%, 70%)`;
        particle.style.borderRadius = '50%';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animation = `float ${Math.random() * 4 + 3}s ease-in-out infinite`;
        particle.style.animationDelay = Math.random() * 3 + 's';
        particle.style.boxShadow = '0 0 10px currentColor';
        particle.style.pointerEvents = 'none';
        container.appendChild(particle);
    }
}

// Initialize all effects
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        createMatrixRain();
        createParticles();
        typewriterEffect();
        addGlitchEffect();
    }, 500);
});

// Loading Screen
window.addEventListener('load', function() {
    const loadingScreen = document.createElement('div');
    loadingScreen.className = 'loading-screen';
    loadingScreen.innerHTML = '<div class="loading-text">INITIALIZING SECURE VAULT...</div>';
    document.body.appendChild(loadingScreen);
    
    setTimeout(() => {
        loadingScreen.style.animation = 'fadeInUp 0.8s ease-out reverse';
        setTimeout(() => {
            loadingScreen.remove();
        }, 800);
    }, 2500);
});

// Add sound effects (optional)
function playHoverSound() {
    // Create a subtle hover sound effect
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
}

// Add hover sound to interactive elements
document.addEventListener('DOMContentLoaded', function() {
    const interactiveElements = document.querySelectorAll('.stButton button, .step, .card');
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', playHoverSound);
    });
});
</script>
""",
    unsafe_allow_html=True,
)

# Ultra Header
st.markdown(
    """
    <div class="header">
        <div class="brand">🛡️ Secure Expense Tracker</div>
        <div class="sub">Neon-encrypted • Private Vault • Cyber UI</div>
        <div>
            <span class="status success">🔒 Encrypted</span>
            <span class="status warning">⚡ Real-time</span>
            <span class="status danger">🛡️ Secure</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Session state
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = 1  # 1=OTP, 2=Add, 3=Unlock/View
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False
if "dob_verified" not in st.session_state:
    st.session_state.dob_verified = False


def render_stepper(active_idx: int):
    steps = ["OTP", "Add", "Unlock & View"]
    html_steps = "<div class='stepper'>"
    for i, s in enumerate(steps, start=1):
        cls = "step active" if i == active_idx else "step"
        html_steps += f"<div class='{cls}'>#{i} {s}</div>"
    html_steps += "</div>"
    st.markdown(html_steps, unsafe_allow_html=True)


# -----------------------------
# PAGE 1 — OTP
# -----------------------------
if st.session_state.page == 1:
    render_stepper(1)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔐 Step 1 — Access OTP")
    st.markdown("Enter your email to receive a secure one-time password for vault access.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        email_input = st.text_input("📧 Enter email to receive OTP", placeholder="you@example.com")
        if st.button("🚀 Send OTP", key="send_otp"):
            if not email_input or "@" not in email_input:
                st.error("❌ Please enter a valid email address.")
            else:
                with st.spinner("🔐 Generating secure OTP..."):
                    otp = generate_otp()
                    st.session_state.generated_otp = otp
                    if DEV_MODE:
                        st.info(f"🔑 Dev OTP: **{otp}**")
                        st.success("✅ OTP generated (dev mode).")
                    else:
                        sent = send_otp_via_smtp(email_input, otp)
                        if sent:
                            st.success("✅ OTP sent — check your inbox/spam.")
                        else:
                            st.error("❌ Failed to send OTP. Please try again.")
    
    with col2:
        entered_otp = st.text_input("🔢 Enter received OTP", placeholder="123456")
        if st.button("🔓 Verify OTP", key="verify_otp"):
            if entered_otp and st.session_state.generated_otp and entered_otp == st.session_state.generated_otp:
                st.session_state.otp_verified = True
                st.session_state.page = 2
                st.success("🎉 OTP Verified — Welcome to your vault!")
                st.rerun()
            else:
                st.error("❌ Invalid OTP. Please check and try again.")
    
    # Security tips
    st.info("🔒 **Security Tips:** OTP expires after 10 minutes • Never share your OTP • Check spam folder if not received")
    st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# PAGE 2 — Add Expense + HUD
# -----------------------------
elif st.session_state.page == 2 and st.session_state.otp_verified:
    render_stepper(2)
    left, right = st.columns([2, 3])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💰 Add Expense")
        st.markdown("Securely add your expenses to the encrypted vault.")
        
        category = st.text_input("📂 Category", placeholder="Food, Travel, Bills, Shopping...")
        amount = st.number_input("💵 Amount (₹)", min_value=0.0, format="%.2f", step=0.01)
        description = st.text_area("📝 Description (optional)", height=90, placeholder="Add any additional details about this expense...")
        
        if st.button("🔒 Add to Vault", key="add_expense"):
            if not category or amount <= 0:
                st.error("❌ Please provide a category and amount > 0.")
            else:
                with st.spinner("🔐 Encrypting and storing..."):
                    add_expense(category.strip(), float(amount), description.strip())
                    st.success("✅ Expense added & encrypted successfully!")
                    st.balloons()
        
        st.caption("🔐 All amounts are encrypted with your local key (secret.key).")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Vault HUD")
        st.markdown("Live statistics from your encrypted expense vault.")
        
        rows = fetch_expenses()
        total_count, total_amount, unique_cats = compute_stats(rows)
        
        # Enhanced stats display
        stats_html = f"""
        <div class='stats-grid'>
            <div class='stat-card'>
                <div class='stat-value'>{total_count}</div>
                <div class='stat-label'>📈 Records</div>
            </div>
            <div class='stat-card'>
                <div class='stat-value'>₹{total_amount:,.2f}</div>
                <div class='stat-label'>💰 Total</div>
            </div>
            <div class='stat-card'>
                <div class='stat-value'>{unique_cats}</div>
                <div class='stat-label'>📂 Categories</div>
            </div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)

        # Recent activity
        if rows:
            st.subheader("🕒 Recent Activity")
            for i, (rid, cat, amt, desc) in enumerate(rows[:3]):
                st.write(f"**{cat}** - ₹{amt}")
                if desc:
                    st.caption(desc)

        if st.button("🔓 Proceed to Unlock & View", key="proceed_view"):
            st.session_state.page = 3
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# PAGE 3 — Unlock & View
# -----------------------------
elif st.session_state.page == 3:
    render_stepper(3)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔓 Unlock Vault — Verify DOB")
    st.markdown("Enter your date of birth to decrypt and view your expense data.")
    
    dob_input = st.text_input("🎂 Enter DOB (dd-mm-yyyy)", type="password", placeholder="dd-mm-yyyy")
    if st.button("🔓 Unlock Vault", key="unlock_vault"):
        if dob_input and dob_input.strip():
            st.session_state.dob_verified = True
            st.success("🎉 Vault unlocked successfully!")
        else:
            st.error("❌ Please enter DOB to unlock.")

    if st.session_state.dob_verified:
        expenses = fetch_expenses()
        if not expenses:
            st.info("📭 No expenses recorded yet. Add some expenses to see them here!")
        else:
            st.subheader("📊 Expense Records")
            
            # Enhanced summary stats
            total_count, total_amount, unique_cats = compute_stats(expenses)
            stats_html = f"""
            <div class='stats-grid'>
                <div class='stat-card'>
                    <div class='stat-value'>{total_count}</div>
                    <div class='stat-label'>📈 Records</div>
                </div>
                <div class='stat-card'>
                    <div class='stat-value'>₹{total_amount:,.2f}</div>
                    <div class='stat-label'>💰 Total</div>
                </div>
                <div class='stat-card'>
                    <div class='stat-value'>{unique_cats}</div>
                    <div class='stat-label'>📂 Categories</div>
                </div>
            </div>
            """
            st.markdown(stats_html, unsafe_allow_html=True)
            
            # Display expenses in a table
            if expenses:
                df_data = []
                for rid, cat, amt, desc in expenses:
                    df_data.append({
                        "ID": rid,
                        "Category": cat,
                        "Amount (₹)": amt,
                        "Description": desc or "No description"
                    })
                
                import pandas as pd
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)
            
            st.info("💡 **Tip:** Your data is securely encrypted. Keep your secret.key safe to maintain access.")
            
    st.markdown('</div>', unsafe_allow_html=True)


# Ultra Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #cccccc; font-size: 0.9rem; padding: 2rem; background: rgba(255,255,255,0.02); border-radius: 15px; border: 1px solid var(--border); margin-top: 3rem;">
        <div style="margin-bottom: 1rem; font-weight: 700; letter-spacing: 2px;">🔐 Keep <code>secret.key</code> safe. If lost, old encrypted data cannot be recovered.</div>
        <div style="font-size: 0.8rem; opacity: 0.7; letter-spacing: 1px;">🛡️ Secure Expense Tracker v3.0 • Built with Streamlit & Fernet Encryption</div>
    </div>
    """, 
    unsafe_allow_html=True
)


