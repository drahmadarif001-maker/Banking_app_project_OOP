# 🏦 Khyber Bank – Online Banking Web Application

A simple, functional online banking system built with **Flask** (Python) and **MySQL**. It simulates core banking operations: account management, deposits, withdrawals, fund transfers, and transaction history.

## ✨ Features

- **User Authentication** – Sign up / Login with account number and password.
- **Dashboard** – View account balance and perform actions.
- **Deposit Money** – Add funds to your account.
- **Withdraw Money** – Withdraw funds with balance validation.
- **Send Money** – Transfer money to another registered account.
- **Transaction History** – View all deposits, withdrawals, and transfers.
- **Account Info** – See your profile details.
- **Logout** – End session securely.

## 🛠️ Tech Stack

| Layer       | Technology                    |
|-------------|-------------------------------|
| Backend     | Python 3.14+ / Flask          |
| Database    | MySQL (mysql-connector-python)|
| Frontend    | HTML5, CSS, Jinja2 templates  |
| Server      | Flask development server      |

## 📁 Database Schema

### `accounts`
- `account_number` (INT, PRIMARY KEY)
- `name` (VARCHAR)
- `age` (INT)
- `password` (VARCHAR)
- `account_type` (VARCHAR)
- `balance` (FLOAT)

### `transaction_history`
- `id` (INT, AUTO_INCREMENT)
- `sender_acc` (INT)
- `receiver_acc` (INT)
- `amount` (FLOAT)
- `transaction_type` (VARCHAR)
- `transaction_date` (TIMESTAMP)

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server (XAMPP/WAMP or standalone)
- Git (optional)

