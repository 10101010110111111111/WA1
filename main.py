#!/usr/bin/env python3
"""
Main script to start the Invoice Management System
"""

import threading
import time
import requests
from app import start_server
import signal
import sys


def wait_for_server(port=80, timeout=30):
    """Wait for the server to start"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f'http://localhost:{port}/', timeout=1)
            if response.status_code == 200:
                print(f"✓ Server is running on port {port}")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def start_system():
    """Start the database and API server"""
    print("Starting Invoice Management System...")

    # Start the server in a separate thread
    server_thread = threading.Thread(
        target=start_server,
        kwargs={'host': '0.0.0.0', 'port': 80, 'debug': False}
    )
    server_thread.daemon = True
    server_thread.start()

    # Wait for server to start
    if wait_for_server(port=80):
        print("✓ System started successfully!")
        print("✓ API is available at http://localhost:80")
        print("✓ Use the following credentials to log in:")
        print("  Owner: username 'owner', password 'owner123'")
        print("  Accountant: username 'accountant', password 'accountant123'")
        print("✓ Press Ctrl+C to stop the server")

        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            sys.exit(0)
    else:
        print("✗ Failed to start server within timeout period")
        sys.exit(1)


if __name__ == '__main__':
    start_system()