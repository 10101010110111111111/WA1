import functools
import re
from flask import Flask, request, session, jsonify
from flask_cors import CORS
from database import Database
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app)  # Enable CORS for all routes

# Initialize database
db = Database()


def require_auth(roles=None):
    """Decorator to require authentication and specific roles"""

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return {"error": "Authentication required"}, 401

            user = db.get_user_by_id(session['user_id'])
            if not user:
                return {"error": "User not found"}, 404

            if roles and user['role'] not in roles:
                return {"error": "Insufficient permissions"}, 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# === AUTHENTICATION ENDPOINTS ===
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return {"error": "Username and password are required"}, 400

    user = db.get_user_by_username(data['username'])
    if user and user['password'] == Database.hash_password(data['password']):
        session['user_id'] = user['id']
        session['user_role'] = user['role']
        return {
            "message": "Login successful",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "role": user['role']
            }
        }
    else:
        return {"error": "Invalid credentials"}, 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return {"message": "Logout successful"}


@app.route('/api/me', methods=['GET'])
@require_auth()
def get_current_user():
    """Get current logged-in user info"""
    user = db.get_user_by_id(session['user_id'])
    if user:
        return {
            "id": user['id'],
            "username": user['username'],
            "role": user['role']
        }
    return {"error": "User not found"}, 404


# === INVOICE ENDPOINTS ===
@app.route('/api/invoices', methods=['GET'])
@require_auth()
def get_invoices():
    """Get all invoices"""
    invoices = db.get_all_invoices()
    return {"invoices": invoices}


@app.route('/api/invoices', methods=['POST'])
@require_auth(roles=['owner', 'accountant'])
def create_invoice():
    """Create new invoice"""
    data = request.get_json()
    if not data or 'invoice_number' not in data or 'customer_name' not in data:
        return {"error": "Invoice number and customer name are required"}, 400

    # Check if invoice number already exists
    existing = db.get_invoice_by_number(data['invoice_number'])
    if existing:
        return {"error": "Invoice number already exists"}, 400

    # Automatically calculate due date as 14 days after issue date if not provided
    if 'issue_date' in data and 'due_date' not in data:
        try:
            issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d')
            due_date = issue_date + timedelta(days=14)
            data['due_date'] = due_date.strftime('%Y-%m-%d')
        except ValueError:
            return {"error": "Invalid issue date format. Use YYYY-MM-DD"}, 400

    try:
        new_invoice = db.create_invoice(data)
        return new_invoice, 201
    except Exception as e:
        return {"error": f"Failed to create invoice: {str(e)}"}, 400


@app.route('/api/invoices/<int:invoice_id>', methods=['GET'])
@require_auth()
def get_invoice(invoice_id):
    """Get specific invoice"""
    invoice = db.get_invoice_by_id(invoice_id)
    if invoice:
        return invoice
    else:
        return {"error": "Invoice not found"}, 404


@app.route('/api/invoices/<int:invoice_id>', methods=['PUT'])
@require_auth(roles=['owner', 'accountant'])
def update_invoice(invoice_id):
    """Update invoice"""
    invoice = db.get_invoice_by_id(invoice_id)
    if not invoice:
        return {"error": "Invoice not found"}, 404

    data = request.get_json()
    
    # Automatically calculate due date as 14 days after issue date if issue_date is updated but due_date is not
    if 'issue_date' in data and 'due_date' not in data:
        try:
            issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d')
            due_date = issue_date + timedelta(days=14)
            data['due_date'] = due_date.strftime('%Y-%m-%d')
        except ValueError:
            return {"error": "Invalid issue date format. Use YYYY-MM-DD"}, 400

    try:
        updated_invoice = db.update_invoice(invoice_id, data)
        if updated_invoice:
            return updated_invoice
        else:
            return {"error": "Failed to update invoice"}, 400
    except Exception as e:
        return {"error": f"Failed to update invoice: {str(e)}"}, 400


@app.route('/api/invoices/<int:invoice_id>', methods=['DELETE'])
@require_auth(roles=['owner'])
def delete_invoice(invoice_id):
    """Delete invoice (owner only)"""
    invoice = db.get_invoice_by_id(invoice_id)
    if not invoice:
        return {"error": "Invoice not found"}, 404

    if db.delete_invoice(invoice_id):
        return {"message": "Invoice deleted successfully"}
    else:
        return {"error": "Failed to delete invoice"}, 400


# === REPORT ENDPOINTS ===
@app.route('/api/reports/unpaid', methods=['GET'])
@require_auth()
def get_unpaid_invoices():
    """Get all unpaid invoices"""
    unpaid_invoices = db.get_unpaid_invoices()
    return {"invoices": unpaid_invoices}


@app.route('/api/reports/largest-debtors', methods=['GET'])
@require_auth()
def get_largest_debtors():
    """Get largest debtors by total unpaid amount"""
    debtors = db.get_largest_debtors()
    return {"debtors": debtors}


@app.route('/api/reports/average-payment-time', methods=['GET'])
@require_auth()
def get_average_payment_time():
    """Get average payment time"""
    avg_time = db.get_average_payment_time()
    return {"average_payment_days": avg_time}


@app.route('/api/reports/overdue', methods=['GET'])
@require_auth()
def get_overdue_invoices():
    """Get overdue invoices"""
    overdue_invoices = db.get_overdue_invoices()
    return {"invoices": overdue_invoices}


@app.route('/')
def index():
    return 'Vitejte v systemu Evidence Faktur'


def start_server(host='0.0.0.0', port=80, debug=False):
    """Start the Flask server"""
    db.initialize_sample_data()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    start_server()