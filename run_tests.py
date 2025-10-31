#!/usr/bin/env python3
"""
Test runner script for the Items API
"""

import subprocess
import sys

def run_tests():
    """Run all tests and display results"""
    print("Running API tests...\n")
    
    # Run tests with unittest
    print("1. Running tests with unittest:")
    print("-" * 40)
    result = subprocess.run([sys.executable, "test_items_api.py"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Run tests with pytest (if available)
    print("\n2. Running tests with pytest:")
    print("-" * 40)
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "test_items_api.py", "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr and "DeprecationWarning" not in result.stderr:
            print("STDERR:", result.stderr)
    except FileNotFoundError:
        print("pytest not found, skipping...")
    
    print("\nTest execution completed!")

if __name__ == "__main__":
    run_tests()