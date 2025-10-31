import sqlite3
import hashlib
import datetime
from typing import List, Dict, Any, Optional


class Database:
    def __init__(self, db_path: str = 'invoices.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn

    def init_db(self):
        """Initialize database tables for invoice management"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table for owner and accountant roles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL, -- 'owner' or 'accountant'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Invoices table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    issue_date DATE NOT NULL,
                    due_date DATE NOT NULL,
                    customer_name TEXT NOT NULL,
                    customer_ic TEXT, -- IČ (identification number)
                    customer_dic TEXT, -- DIČ (VAT identification number)
                    customer_address TEXT,
                    total_amount REAL NOT NULL, -- Total amount including VAT
                    payment_status TEXT NOT NULL DEFAULT 'nezaplaceno', -- 'zaplaceno' or 'nezaplaceno'
                    payment_date DATE, -- Date when paid
                    service_description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()

    def initialize_sample_data(self):
        """Initialize sample data for the invoice system"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] > 0:
                return  # Data already initialized

            # Add sample users
            users = [
                ("owner", self.hash_password("owner123"), "owner"),
                ("accountant", self.hash_password("accountant123"), "accountant")
            ]
            cursor.executemany(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                users
            )

            # Add sample invoices
            invoices = [
                ("F2025001", "2025-10-01", "2025-10-15", "ABC Company s.r.o.", "12345678", "CZ12345678", 
                 "Main Street 123, Prague", 15000.0, "zaplaceno", "2025-10-10", "IT consulting services"),
                ("F2025002", "2025-10-05", "2025-10-19", "XYZ Solutions a.s.", "87654321", "CZ87654321",
                 "Business Park 456, Brno", 22000.0, "nezaplaceno", None, "Software development"),
                ("F2025003", "2025-10-10", "2025-10-24", "Tech Innovations s.r.o.", "11223344", "CZ11223344",
                 "Innovation Street 789, Ostrava", 18000.0, "zaplaceno", "2025-10-20", "Technical support")
            ]
            cursor.executemany(
                '''INSERT INTO invoices 
                (invoice_number, issue_date, due_date, customer_name, customer_ic, customer_dic, 
                customer_address, total_amount, payment_status, payment_date, service_description) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                invoices
            )

            conn.commit()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return hashlib.sha256(password.encode()).hexdigest()

    # User methods
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_user(self, username: str, password: str, role: str) -> Dict[str, Any]:
        """Create new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, self.hash_password(password), role)
            )
            user_id = cursor.lastrowid
            conn.commit()

            return {
                "id": user_id,
                "username": username,
                "role": role
            }

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (without passwords)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, created_at FROM users")
            return [dict(row) for row in cursor.fetchall()]

    def update_user_password(self, user_id: int, new_password: str):
        """Update user password"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (self.hash_password(new_password), user_id)
            )
            conn.commit()

    # Invoice methods
    def get_all_invoices(self) -> List[Dict[str, Any]]:
        """Get all invoices"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices ORDER BY issue_date DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_invoice_by_id(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Get invoice by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get invoice by invoice number"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new invoice"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO invoices 
                (invoice_number, issue_date, due_date, customer_name, customer_ic, customer_dic, 
                customer_address, total_amount, payment_status, payment_date, service_description) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    invoice_data['invoice_number'],
                    invoice_data['issue_date'],
                    invoice_data['due_date'],
                    invoice_data['customer_name'],
                    invoice_data.get('customer_ic'),
                    invoice_data.get('customer_dic'),
                    invoice_data.get('customer_address'),
                    invoice_data['total_amount'],
                    invoice_data.get('payment_status', 'nezaplaceno'),
                    invoice_data.get('payment_date'),
                    invoice_data.get('service_description')
                )
            )
            invoice_id = cursor.lastrowid
            conn.commit()

            # Return the created invoice
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
            return dict(cursor.fetchone())

    def update_invoice(self, invoice_id: int, invoice_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update invoice"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query based on provided fields
            fields = []
            values = []
            
            for key, value in invoice_data.items():
                if key in ['invoice_number', 'issue_date', 'due_date', 'customer_name', 'customer_ic', 
                          'customer_dic', 'customer_address', 'total_amount', 'payment_status', 
                          'payment_date', 'service_description']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return None
                
            # Add updated_at timestamp
            fields.append("updated_at = ?")
            values.append(datetime.datetime.now())
            
            # Add invoice_id for WHERE clause
            values.append(invoice_id)
            
            query = f"UPDATE invoices SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()

            # Return the updated invoice
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_invoice(self, invoice_id: int) -> bool:
        """Delete invoice"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_unpaid_invoices(self) -> List[Dict[str, Any]]:
        """Get all unpaid invoices"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE payment_status = 'nezaplaceno' ORDER BY due_date ASC")
            return [dict(row) for row in cursor.fetchall()]

    def get_largest_debtors(self) -> List[Dict[str, Any]]:
        """Get largest debtors by total unpaid amount"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT customer_name, SUM(total_amount) as total_debt
                FROM invoices 
                WHERE payment_status = 'nezaplaceno'
                GROUP BY customer_name
                ORDER BY total_debt DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_average_payment_time(self) -> float:
        """Calculate average payment time in days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT AVG(julianday(payment_date) - julianday(issue_date)) as avg_payment_days
                FROM invoices 
                WHERE payment_status = 'zaplaceno' AND payment_date IS NOT NULL
            ''')
            row = cursor.fetchone()
            return row[0] if row and row[0] else 0.0

    def get_overdue_invoices(self) -> List[Dict[str, Any]]:
        """Get overdue invoices (not paid and past due date)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT *, julianday('now') - julianday(due_date) as days_overdue
                FROM invoices 
                WHERE payment_status = 'nezaplaceno' AND due_date < date('now')
                ORDER BY due_date ASC
            ''')
            return [dict(row) for row in cursor.fetchall()]