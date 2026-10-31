
import sqlite3
import sys
from datetime import datetime

DB_NAME = "electricity_billing.db"
RATE_PER_UNIT = 5.0

# DATABASE CONNECTION

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# DATABASE INITIALIZATION

def initialize_database():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Table 1: Users
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """)

            # Table 2: Consumers (NEW)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consumers (
                    consumer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    consumer_number TEXT UNIQUE NOT NULL,
                    consumer_name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE SET NULL
                )
            """)

            # Table 3: Bills
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bills (
                    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    consumer_number TEXT NOT NULL,
                    consumer_name TEXT NOT NULL,
                    units_consumed REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'Unpaid',
                    FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Table 4: Payments (NEW)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER NOT NULL UNIQUE,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    payment_date TEXT NOT NULL,
                    FOREIGN KEY (bill_id)
                    REFERENCES bills(bill_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id)
                    REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Default Admin
            cursor.execute(
                "SELECT id FROM users WHERE username = 'admin'"
            )

            if not cursor.fetchone():
                cursor.execute(
                    """INSERT INTO users
                    (username, password, role)
                    VALUES (?, ?, ?)""",
                    ("admin", "admin123", "Admin")
                )
                print("[Info] Default Admin created.")
                print("Username: admin")
                print("Password: admin123")

            conn.commit()
            print("[Info] Database initialized successfully.")

    except sqlite3.Error as e:
        print("[Database Error]", e)


# INPUT VALIDATION

def get_non_empty_input(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("[Error] Input cannot be empty.")


def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))

            if 0 <= value < float("inf"):
                return value

            print("[Error] Enter a valid non-negative number.")

        except ValueError:
            print("[Error] Please enter a number.")


def get_integer_input(prompt):
    while True:
        try:
            return int(input(prompt))

        except ValueError:
            print("[Error] Please enter a valid integer.")


# USER REGISTRATION


def register_user():
    print("\n--- Customer Registration ---")

    username = get_non_empty_input("Enter username: ")
    password = get_non_empty_input("Enter password: ")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """INSERT INTO users
                (username, password, role)
                VALUES (?, ?, ?)""",
                (username, password, "Customer")
            )

            conn.commit()

            print("[Success] Registration completed.")

    except sqlite3.IntegrityError:
        print("[Error] Username already exists.")

    except sqlite3.Error as e:
        print("[Database Error]", e)

# USER LOGIN

def login_user():
    print("\n--- User Login ---")

    username = get_non_empty_input("Username: ")
    password = get_non_empty_input("Password: ")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """SELECT id, username, role
                FROM users
                WHERE username = ? AND password = ?""",
                (username, password)
            )

            user = cursor.fetchone()

        if user:
            print("\nWelcome", user[1])

            if user[2] == "Admin":
                admin_menu(user[0])
            else:
                customer_menu(user[0])

        else:
            print("[Error] Invalid username or password.")

    except sqlite3.Error as e:
        print("[Database Error]", e)


# ADMIN MENU

def admin_menu(admin_id):
    while True:
        print("\n========== ADMIN MENU ==========")
        print("1. Add Consumer")
        print("2. View All Consumers")
        print("3. Create Bill")
        print("4. View All Bills")
        print("5. Update Bill")
        print("6. Delete Bill")
        print("7. View All Users")
        print("8. View Payment History")
        print("9. Logout")

        choice = get_integer_input("Enter choice: ")

        if choice == 1:
            add_consumer()
        elif choice == 2:
            view_all_consumers()
        elif choice == 3:
            create_bill()
        elif choice == 4:
            view_all_bills()
        elif choice == 5:
            update_bill()
        elif choice == 6:
            delete_bill()
        elif choice == 7:
            view_all_users()
        elif choice == 8:
            view_payment_history()
        elif choice == 9:
            print("Admin logged out.")
            break
        else:
            print("Invalid choice.")

# ADD CONSUMER (NEW)

def add_consumer():
    print("\n--- Add New Consumer ---")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """SELECT id, username FROM users
                WHERE role = 'Customer'"""
            )

            customers = cursor.fetchall()

            if customers:
                print("\nRegistered Customers:")

                for customer in customers:
                    print(customer[0], "-", customer[1])

                user_id = get_integer_input(
                    "Enter Customer User ID (0 for unlinked): "
                )

                if user_id == 0:
                    user_id = None
                elif user_id not in [c[0] for c in customers]:
                    print("[Error] Invalid Customer User ID.")
                    return
            else:
                user_id = None

            consumer_number = get_non_empty_input(
                "Enter Consumer Number: "
            )

            consumer_name = get_non_empty_input(
                "Enter Consumer Name: "
            )

            address = get_non_empty_input(
                "Enter Address: "
            )

            cursor.execute(
                """INSERT INTO consumers
                (user_id, consumer_number, consumer_name, address)
                VALUES (?, ?, ?, ?)""",
                (user_id, consumer_number,
                 consumer_name, address)
            )

            conn.commit()

            print("[Success] Consumer added successfully.")

    except sqlite3.IntegrityError:
        print("[Error] Consumer number already exists.")

    except sqlite3.Error as e:
        print("[Database Error]", e)


# VIEW ALL CONSUMERS (NEW)

def view_all_consumers():
    print("\n--- Consumer Details ---")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT consumer_id, consumer_number,
                       consumer_name, address
                FROM consumers
            """)

            consumers = cursor.fetchall()

            if not consumers:
                print("No consumers found.")
                return

            for c in consumers:
                print("------------------------------")
                print("Consumer ID:", c[0])
                print("Consumer Number:", c[1])
                print("Consumer Name:", c[2])
                print("Address:", c[3])

    except sqlite3.Error as e:
        print("[Database Error]", e)

# CREATE BILL


def create_bill():
    print("\n--- Create Electricity Bill ---")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT consumer_number, consumer_name
                FROM consumers
            """)

            consumers = cursor.fetchall()

            if not consumers:
                print("[Info] Add a consumer first.")
                return

            print("\nAvailable Consumers:")

            for c in consumers:
                print(c[0], "-", c[1])

            consumer_number = get_non_empty_input(
                "Enter Consumer Number: "
            )

            cursor.execute(
                """SELECT user_id, consumer_name
                FROM consumers
                WHERE consumer_number = ?""",
                (consumer_number,)
            )

            consumer = cursor.fetchone()

            if not consumer:
                print("[Error] Consumer not found.")
                return

            user_id = consumer[0]
            consumer_name = consumer[1]

            units = get_positive_float(
                "Enter Units Consumed: "
            )

            total_amount = units * RATE_PER_UNIT

            cursor.execute(
                """INSERT INTO bills
                (user_id, consumer_number,
                 consumer_name, units_consumed,
                 total_amount, status)
                VALUES (?, ?, ?, ?, ?, 'Unpaid')""",
                (user_id, consumer_number,
                 consumer_name, units, total_amount)
            )

            conn.commit()

            print("[Success] Bill created.")
            print("Units Consumed:", units)
            print("Total Amount: Rs.", format(total_amount, ".2f"))

    except sqlite3.Error as e:
        print("[Database Error]", e)

# VIEW ALL BILLS

def view_all_bills():
    print("\n--- All Electricity Bills ---")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT bill_id, consumer_number,
                       consumer_name, units_consumed,
                       total_amount, status
                FROM bills
            """)

            bills = cursor.fetchall()

            if not bills:
                print("No bills found.")
                return

            for b in bills:
                print("------------------------------")
                print("Bill ID:", b[0])
                print("Consumer Number:", b[1])
                print("Consumer Name:", b[2])
                print("Units:", b[3])
                print("Amount: Rs.", b[4])
                print("Status:", b[5])

    except sqlite3.Error as e:
        print("[Database Error]", e)


# UPDATE BILL

def update_bill():
    print("\n--- Update Bill ---")

    bill_id = get_integer_input("Enter Bill ID: ")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """SELECT status FROM bills
                WHERE bill_id = ?""",
                (bill_id,)
            )

            bill = cursor.fetchone()

            if not bill:
                print("[Error] Bill not found.")
                return

            if bill[0] == "Paid":
                print("[Error] Paid bills cannot be modified.")
                return

            units = get_positive_float(
                "Enter New Units Consumed: "
            )

            amount = units * RATE_PER_UNIT

            cursor.execute(
                """UPDATE bills
                SET units_consumed = ?,
                    total_amount = ?
                WHERE bill_id = ?""",
                (units, amount, bill_id)
            )

            conn.commit()

            print("[Success] Bill updated.")
            print("New Amount: Rs.", amount)

    except sqlite3.Error as e:
        print("[Database Error]", e)

# DELETE BILL

def delete_bill():
    print("\n--- Delete Bill ---")

    bill_id = get_integer_input("Enter Bill ID: ")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT status FROM bills WHERE bill_id = ?",
                (bill_id,)
            )

            bill = cursor.fetchone()

            if not bill:
                print("[Error] Bill not found.")
                return

            if bill[0] == "Paid":
                print("[Error] Paid bills cannot be deleted.")
                return

            cursor.execute(
                "DELETE FROM bills WHERE bill_id = ?",
                (bill_id,)
            )

            conn.commit()

            print("[Success] Bill deleted.")

    except sqlite3.Error as e:
        print("[Database Error]", e)


# VIEW USERS

def view_all_users():
    print("\n--- Registered Users ---")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, username, role FROM users"
            )

            users = cursor.fetchall()

            for u in users:
                print(
                    "ID:", u[0],
                    "| Username:", u[1],
                    "| Role:", u[2]
                )

    except sqlite3.Error as e:
        print("[Database Error]", e)

# VIEW PAYMENT HISTORY (NEW)

def view_payment_history():
    print("\n--- Payment History ---")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT p.payment_id, p.bill_id,
                       u.username, p.amount,
                       p.payment_date
                FROM payments p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.payment_id DESC
            """)

            payments = cursor.fetchall()

            if not payments:
                print("No payments found.")
                return

            for p in payments:
                print("------------------------------")
                print("Payment ID:", p[0])
                print("Bill ID:", p[1])
                print("Customer:", p[2])
                print("Amount: Rs.", p[3])
                print("Payment Date:", p[4])

    except sqlite3.Error as e:
        print("[Database Error]", e)

# CUSTOMER MENU

def customer_menu(customer_id):
    while True:
        print("\n CUSTOMER MENU ")
        print("1. View My Bills")
        print("2. Pay Bill")
        print("3. View My Payment History")
        print("4. Logout")

        choice = get_integer_input("Enter choice: ")

        if choice == 1:
            view_customer_bills(customer_id)
        elif choice == 2:
            pay_customer_bill(customer_id)
        elif choice == 3:
            view_customer_payments(customer_id)
        elif choice == 4:
            print("Customer logged out.")
            break
        else:
            print("Invalid choice.")


# VIEW CUSTOMER BILLS

def view_customer_bills(customer_id):
    print("\n--- My Electricity Bills ---")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """SELECT bill_id, consumer_number,
                          units_consumed, total_amount,
                          status
                FROM bills
                WHERE user_id = ?""",
                (customer_id,)
            )

            bills = cursor.fetchall()

            if not bills:
                print("No bills found.")
                return

            for b in bills:
                print("------------------------------")
                print("Bill ID:", b[0])
                print("Consumer Number:", b[1])
                print("Units:", b[2])
                print("Amount: Rs.", b[3])
                print("Status:", b[4])

    except sqlite3.Error as e:
        print("[Database Error]", e)


# PAY BILL AND RECORD PAYMENT (NEW)


def pay_customer_bill(customer_id):
    print("\n--- Pay Electricity Bill ---")

    view_customer_bills(customer_id)

    bill_id = get_integer_input(
        "Enter Bill ID to Pay: "
    )

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """SELECT total_amount, status
                FROM bills
                WHERE bill_id = ? AND user_id = ?""",
                (bill_id, customer_id)
            )

            bill = cursor.fetchone()

            if not bill:
                print("[Error] Invalid Bill ID.")
                return

            if bill[1] == "Paid":
                print("[Info] Bill already paid.")
                return

            amount = bill[0]

            payment_date = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Insert payment record
            cursor.execute(
                """INSERT INTO payments
                (bill_id, user_id, amount, payment_date)
                VALUES (?, ?, ?, ?)""",
                (bill_id, customer_id,
                 amount, payment_date)
            )

            # Update bill status
            cursor.execute(
                """UPDATE bills
                SET status = 'Paid'
                WHERE bill_id = ? AND user_id = ?""",
                (bill_id, customer_id)
            )

            conn.commit()

            print("[Success] Payment recorded.")
            print("Amount Paid: Rs.", amount)
            print("Payment Date:", payment_date)

    except sqlite3.IntegrityError:
        print("[Error] Payment already recorded.")

    except sqlite3.Error as e:
        print("[Database Error]", e)


# VIEW CUSTOMER PAYMENT HISTORY (NEW)


def view_customer_payments(customer_id):
    print("\n--- My Payment History ---")

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """SELECT payment_id, bill_id,
                          amount, payment_date
                FROM payments
                WHERE user_id = ?
                ORDER BY payment_id DESC""",
                (customer_id,)
            )

            payments = cursor.fetchall()

            if not payments:
                print("No payment history found.")
                return

            for p in payments:
                print("------------------------------")
                print("Payment ID:", p[0])
                print("Bill ID:", p[1])
                print("Amount: Rs.", p[2])
                print("Payment Date:", p[3])

    except sqlite3.Error as e:
        print("[Database Error]", e)


# MAIN APPLICATION


def main():
    initialize_database()

    while True:
        print("\n*****************************************")
        print(" ELECTRICITY BILLING MANAGEMENT SYSTEM")
        print("********************************************")
        print("1. Login")
        print("2. Register Customer")
        print("3. Exit")

        choice = get_integer_input(
            "Select an option (1-3): "
        )

        if choice == 1:
            login_user()
        elif choice == 2:
            register_user()
        elif choice == 3:
            print("Thank you for using the system.")
            sys.exit(0)
        else:
            print("[Error] Invalid choice.")


if __name__ == "__main__":
    main()

