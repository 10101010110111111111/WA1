#!/usr/bin/env python3
"""
Test script for Invoice Management System
Run this script to test all API endpoints
"""

import requests
import json
import sys
from typing import Dict, Any


class InvoiceAPITester:
    def __init__(self, base_url="http://localhost:80"):
        self.base_url = base_url
        self.session = requests.Session()
        self.current_user = None

    def print_response(self, response, message=""):
        """Print formatted response"""
        print(f"\n{'=' * 60}")
        if message:
            print(f"🔹 {message}")
        print(f"URL: {response.url}")
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.text}")
        else:
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Response: {response.text}")
        print(f"{'=' * 60}")
        return response

    def test_connection(self):
        """Test basic server connection"""
        print("🧪 Testing server connection...")
        try:
            response = self.session.get(f"{self.base_url}/")
            self.print_response(response, "Server connection test")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def login(self, username, password):
        """Login with given credentials"""
        print(f"🔐 Logging in as {username}...")
        data = {
            "username": username,
            "password": password
        }
        response = self.session.post(f"{self.base_url}/api/login", json=data)
        result = self.print_response(response, f"Login as {username}")

        if response.status_code == 200:
            self.current_user = response.json().get('user')
            print(f"✅ Logged in as {self.current_user['username']} (role: {self.current_user['role']})")
            return True
        return False

    def logout(self):
        """Logout current user"""
        print("🚪 Logging out...")
        response = self.session.post(f"{self.base_url}/api/logout")
        self.print_response(response, "Logout")
        if response.status_code == 200:
            self.current_user = None
            return True
        return False

    def get_current_user(self):
        """Get current user info"""
        print("👤 Getting current user info...")
        response = self.session.get(f"{self.base_url}/api/me")
        return self.print_response(response, "Get current user")

    # === INVOICE TESTS ===
    def get_invoices(self):
        """Get all invoices"""
        print("🧾 Getting all invoices...")
        response = self.session.get(f"{self.base_url}/api/invoices")
        return self.print_response(response, "Get invoices")

    def create_invoice(self, invoice_data):
        """Create a new invoice"""
        print(f"➕ Creating invoice: {invoice_data['invoice_number']}...")
        response = self.session.post(f"{self.base_url}/api/invoices", json=invoice_data)
        result = self.print_response(response, f"Create invoice: {invoice_data['invoice_number']}")
        return response

    def get_invoice(self, invoice_id):
        """Get specific invoice"""
        print(f"🧾 Getting invoice {invoice_id}...")
        response = self.session.get(f"{self.base_url}/api/invoices/{invoice_id}")
        return self.print_response(response, f"Get invoice {invoice_id}")

    def update_invoice(self, invoice_id, invoice_data):
        """Update invoice"""
        print(f"✏️ Updating invoice {invoice_id}...")
        response = self.session.put(f"{self.base_url}/api/invoices/{invoice_id}", json=invoice_data)
        return self.print_response(response, f"Update invoice {invoice_id}")

    def delete_invoice(self, invoice_id):
        """Delete invoice"""
        print(f"🗑️ Deleting invoice {invoice_id}...")
        response = self.session.delete(f"{self.base_url}/api/invoices/{invoice_id}")
        return self.print_response(response, f"Delete invoice {invoice_id}")

    # === REPORT TESTS ===
    def get_unpaid_invoices(self):
        """Get unpaid invoices"""
        print("🧾 Getting unpaid invoices...")
        response = self.session.get(f"{self.base_url}/api/reports/unpaid")
        return self.print_response(response, "Get unpaid invoices")

    def get_largest_debtors(self):
        """Get largest debtors"""
        print("💰 Getting largest debtors...")
        response = self.session.get(f"{self.base_url}/api/reports/largest-debtors")
        return self.print_response(response, "Get largest debtors")

    def get_average_payment_time(self):
        """Get average payment time"""
        print("⏱️ Getting average payment time...")
        response = self.session.get(f"{self.base_url}/api/reports/average-payment-time")
        return self.print_response(response, "Get average payment time")

    def get_overdue_invoices(self):
        """Get overdue invoices"""
        print("⏰ Getting overdue invoices...")
        response = self.session.get(f"{self.base_url}/api/reports/overdue")
        return self.print_response(response, "Get overdue invoices")

    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive Invoice API Tests")
        print("=" * 80)

        # Test 1: Server connection
        if not self.test_connection():
            print("❌ Server connection failed. Exiting.")
            return False

        # Test 2: Test as owner
        print("\n" + "=" * 80)
        print("👑 TESTING AS OWNER")
        print("=" * 80)

        if not self.login("owner", "owner123"):
            print("❌ Owner login failed")
            return False

        self.get_current_user()
        self.get_invoices()
        self.get_unpaid_invoices()
        self.get_largest_debtors()
        self.get_average_payment_time()
        self.get_overdue_invoices()

        # Create a new invoice as owner
        new_invoice = {
            "invoice_number": "F2025004",
            "issue_date": "2025-10-15",
            "due_date": "2025-10-29",
            "customer_name": "Test Company s.r.o.",
            "customer_ic": "11111111",
            "customer_dic": "CZ11111111",
            "customer_address": "Test Street 1, Prague",
            "total_amount": 25000.0,
            "payment_status": "nezaplaceno",
            "service_description": "Web development services"
        }
        created_invoice = self.create_invoice(new_invoice)
        
        if created_invoice.status_code == 201:
            invoice_id = created_invoice.json().get('id')
            
            # Update the invoice
            update_data = {
                "payment_status": "zaplaceno",
                "payment_date": "2025-10-25"
            }
            self.update_invoice(invoice_id, update_data)
            
            # Get the updated invoice
            self.get_invoice(invoice_id)
            
            # Delete the invoice (owner only)
            self.delete_invoice(invoice_id)

        # Test automatic due date calculation (14 days after issue date)
        print("\n" + "=" * 80)
        print("📅 TESTING AUTOMATIC DUE DATE CALCULATION")
        print("=" * 80)
        
        invoice_with_auto_due_date = {
            "invoice_number": "F2025006",
            "issue_date": "2025-10-20",  # Due date should be automatically set to 2025-11-03 (14 days later)
            "customer_name": "Auto Due Date Test s.r.o.",
            "customer_ic": "33333333",
            "customer_dic": "CZ33333333",
            "customer_address": "Automation Street 3, Prague",
            "total_amount": 15000.0,
            "service_description": "Testing automatic due date calculation"
        }
        auto_due_date_invoice = self.create_invoice(invoice_with_auto_due_date)
        
        if auto_due_date_invoice.status_code == 201:
            invoice_data = auto_due_date_invoice.json()
            print(f"Created invoice with automatic due date:")
            print(f"  Issue date: {invoice_data['issue_date']}")
            print(f"  Due date: {invoice_data['due_date']}")
            
            # Verify the due date is 14 days after issue date
            if invoice_data['due_date'] == "2025-11-03":
                print("✅ Automatic due date calculation works correctly")
            else:
                print("❌ Automatic due date calculation failed")
            
            # Test updating invoice with automatic due date calculation
            update_with_auto_due = {
                "issue_date": "2025-10-25"  # Due date should be automatically set to 2025-11-08
            }
            self.update_invoice(invoice_data['id'], update_with_auto_due)
            
            # Get updated invoice to verify
            updated_invoice = self.get_invoice(invoice_data['id'])
            if updated_invoice.status_code == 200:
                updated_data = updated_invoice.json()
                if updated_data['due_date'] == "2025-11-08":
                    print("✅ Automatic due date calculation on update works correctly")
                else:
                    print("❌ Automatic due date calculation on update failed")

        self.logout()

        # Test 3: Test as accountant
        print("\n" + "=" * 80)
        print("💼 TESTING AS ACCOUNTANT")
        print("=" * 80)

        self.login("accountant", "accountant123")
        self.get_current_user()
        self.get_invoices()
        self.get_unpaid_invoices()
        self.get_largest_debtors()
        self.get_average_payment_time()
        self.get_overdue_invoices()

        # Create a new invoice as accountant
        new_invoice_acc = {
            "invoice_number": "F2025005",
            "issue_date": "2025-10-16",
            "due_date": "2025-10-30",
            "customer_name": "Accountant Test s.r.o.",
            "customer_ic": "22222222",
            "customer_dic": "CZ22222222",
            "customer_address": "Accountant Street 2, Brno",
            "total_amount": 30000.0,
            "payment_status": "nezaplaceno",
            "service_description": "Accounting services"
        }
        created_invoice_acc = self.create_invoice(new_invoice_acc)
        
        if created_invoice_acc.status_code == 201:
            invoice_id = created_invoice_acc.json().get('id')
            
            # Update the invoice
            update_data = {
                "total_amount": 32000.0
            }
            self.update_invoice(invoice_id, update_data)
            
            # Get the updated invoice
            self.get_invoice(invoice_id)
            
            # Try to delete the invoice (should fail as accountant doesn't have permission)
            print("Attempting to delete invoice as accountant (should fail)...")
            self.delete_invoice(invoice_id)

        self.logout()

        # Test 4: Error cases and authentication tests
        print("\n" + "=" * 80)
        print("🚫 TESTING ERROR CASES")
        print("=" * 80)

        # Test accessing protected endpoint without login
        print("Testing access without authentication...")
        self.get_invoices()

        # Test login with wrong credentials
        self.login("owner", "wrongpassword")

        # Test duplicate invoice number
        self.login("owner", "owner123")
        duplicate_invoice = {
            "invoice_number": "F2025001",  # Already exists
            "issue_date": "2025-10-15",
            "due_date": "2025-10-29",
            "customer_name": "Duplicate Test s.r.o.",
            "total_amount": 15000.0
        }
        self.create_invoice(duplicate_invoice)
        self.logout()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        return True


def main():
    """Main function"""
    tester = InvoiceAPITester()

    try:
        success = tester.run_comprehensive_test()
        if success:
            print("🎉 All tests completed successfully!")
        else:
            print("❌ Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()