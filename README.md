# SecureExpenseTracker
 OTP Authentication &amp; End-to-End Encryption
Project Overview
SecureExpenseTracker is a personal expense management web application that ensures the security and privacy of user financial data. It uses email-based OTP authentication for secure login and AES encryption to store sensitive expense information safely. Users can add daily expenses, view monthly summaries, and receive basic spending insights.

Features
Secure login with email OTP verification (no passwords required)

Add, view, and manage daily expenses with encrypted storage

AES encryption for all stored financial data

Monthly expense summaries to track spending

Basic spending insights and suggestions to help manage budget

Built using Python and Streamlit for a clean and interactive UI

Technologies Used
Python

Streamlit (for UI)

Cryptography library (AES encryption)

SMTP (for sending OTP emails)

SQLite (for storing encrypted expense data)

Setup Instructions
Clone this repository:

bash
Copy
Edit
git clone https://github.com/yourusername/SecureExpenseTracker.git  
cd SecureExpenseTracker  
Install dependencies:

bash
Copy
Edit
pip install -r requirements.txt  
Configure email SMTP settings in the config file (for OTP sending).

Run the app:

bash
Copy
Edit
streamlit run app.py  
Usage
Enter your email to receive an OTP for login.

Verify OTP to access the app.

Add your expenses by providing date, description, and amount.

View monthly summaries and basic insights on spending habits.

Future Enhancements
Add export/import functionality for expense data

Integrate AI-driven personalized financial advice

Support for expense categories and automatic classification

License
This project is licensed under the MIT License.
