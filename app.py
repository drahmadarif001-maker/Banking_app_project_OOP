from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change for production

# Custom Jinja2 filter for number formatting
@app.template_filter('format_number')
def format_number(value):
    try:
        return f"{value:,.2f}"
    except:
        return str(value)
# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Ahmadarif1122',
    'database': 'khyber_bank'
}


# ------------------- Database Initialization -------------------
def init_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Ahmadarif1122'
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS khyber_bank")
    cursor.execute("USE khyber_bank")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_number INT PRIMARY KEY,
        name VARCHAR(100),
        age INT,
        password VARCHAR(50),
        account_type VARCHAR(20),
        balance FLOAT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaction_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sender_acc INT,
        receiver_acc INT,
        amount FLOAT,
        transaction_type VARCHAR(50),
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

    # Call the function to create tables (if not exist)
    init_db()

    # ------------------- Helper Functions -------------------


def get_db_connection():
    return mysql.connector.connect(**db_config)


def get_user_by_acc(acc_number):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM accounts WHERE account_number = %s", (acc_number,))
    user = cursor.fetchone()
    conn.close()
    return user


def update_balance(acc_number, new_balance):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE accounts SET balance = %s WHERE account_number = %s", (new_balance, acc_number))
    conn.commit()
    conn.close()


def add_transaction(sender, receiver, amount, trans_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO transaction_history (sender_acc, receiver_acc, amount, transaction_type)
    VALUES (%s, %s, %s, %s)
    """, (sender, receiver, amount, trans_type))
    conn.commit()
    conn.close()

    # ------------------- Routes -------------------


@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        acc_no = request.form['account_number']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s AND password = %s",
            (acc_no, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['account_number']
            session['user_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))   # ✅ returns a response
        else:
            flash('Invalid account number or password.', 'danger')
            return redirect(url_for('login'))       # ✅ returns a response

        # GET request (or any other method) – show the login form
    return render_template('login.html')            # ✅ returns a response


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        acc_type = request.form['account_type']
        initial_deposit = request.form['initial_deposit']

        # Validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))

        try:
            age = int(age)
            initial_deposit = float(initial_deposit)
            if initial_deposit < 0:
                raise ValueError
        except ValueError:
            flash('Invalid age or deposit amount.', 'danger')
            return redirect(url_for('signup'))

        # Generate unique account number
        acc_number = random.randint(100000, 999999)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO accounts (account_number, name, age, password, account_type, balance)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (acc_number, name, age, password, acc_type, initial_deposit))
            conn.commit()
            flash(
                f'Account created successfully! Your account number is {acc_number}', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
            return redirect(url_for('signup'))
        
      
        finally:
         conn.close()

        # GET request
    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = get_user_by_acc(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    return render_template('dashboard.html', user=user)


@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        amount = float(request.form['amount'])
    except ValueError:
        flash('Invalid amount. Please enter a number.', 'danger')
        return redirect(url_for('dashboard'))

    if amount <= 0:
        flash('Amount must be positive.', 'danger')
        return redirect(url_for('dashboard'))

    user = get_user_by_acc(session['user_id'])
    new_balance = user['balance'] + amount
    update_balance(session['user_id'], new_balance)
    add_transaction(session['user_id'], session['user_id'], amount, 'Deposit')

    flash(f'Successfully deposited PKR {amount:,.2f}', 'success')
    return redirect(url_for('dashboard'))


@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        amount = float(request.form['amount'])
    except ValueError:
        flash('Invalid amount. Please enter a number.', 'danger')
        return redirect(url_for('dashboard'))

    user = get_user_by_acc(session['user_id'])

    if amount <= 0:
        flash('Amount must be positive.', 'danger')
    elif amount > user['balance']:
        flash('Insufficient balance.', 'danger')
    else:
        new_balance = user['balance'] - amount
        update_balance(session['user_id'], new_balance)
        add_transaction(session['user_id'],
                        session['user_id'], amount, 'Withdraw')
        flash(f'Successfully withdrew PKR {amount:,.2f}', 'success')

        return redirect(url_for('dashboard'))


@app.route('/send', methods=['GET', 'POST'])
def send_money():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            receiver_acc = int(request.form['receiver_account'])
            amount = float(request.form['amount'])
        except ValueError:
            flash('Invalid input. Please enter valid numbers.', 'danger')
            return render_template('send_money.html')

        user = get_user_by_acc(session['user_id'])

        if amount <= 0:
            flash('Amount must be positive.', 'danger')
        elif amount > user['balance']:
            flash('Insufficient balance.', 'danger')
        else:
            receiver = get_user_by_acc(receiver_acc)
            if not receiver:
                flash('Receiver account not found.', 'danger')
            else:
                # Perform transfer
                new_sender_balance = user['balance'] - amount
                new_receiver_balance = receiver['balance'] + amount
                update_balance(session['user_id'], new_sender_balance)
                update_balance(receiver_acc, new_receiver_balance)
                add_transaction(session['user_id'],
                                receiver_acc, amount, 'Send Money')
                flash(
                    f'Successfully sent PKR {amount:,.2f} to {receiver["name"]} (Acc: {receiver_acc})', 'success')
            return redirect(url_for('dashboard'))

            # If we reach here, something failed (invalid amount, balance, or receiver)
        return render_template('send_money.html')

            # GET request
    return render_template('send_money.html')


@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT transaction_type, sender_acc, receiver_acc, amount, transaction_date
    FROM transaction_history
    WHERE sender_acc = %s OR receiver_acc = %s
    ORDER BY id DESC
    """, (session['user_id'], session['user_id']))
    transactions = cursor.fetchall()
    conn.close()

    return render_template('history.html', transactions=transactions)


@app.route('/account_info')
def account_info():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = get_user_by_acc(session['user_id'])
    return render_template('account_info.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
