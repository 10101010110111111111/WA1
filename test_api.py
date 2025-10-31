import requests
import json

# Base URL of the API
base_url = "http://127.0.0.1:5000"

# Test creating an item
print("Creating a new item...")
create_data = {
    "title": "Koupit mléko",
    "description": "Plnotučné",
    "done": False
}
response = requests.post(f"{base_url}/items", json=create_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

# Get the ID of the created item
item_id = response.json()['id']

# Test getting all items
print("\nGetting all items...")
response = requests.get(f"{base_url}/items")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

# Test getting a specific item
print("\nGetting a specific item...")
response = requests.get(f"{base_url}/items/{item_id}")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

# Test updating an item
print("\nUpdating an item...")
update_data = {
    "title": "Koupit chléb",
    "description": "Celozrnný",
    "done": True
}
response = requests.put(f"{base_url}/items/{item_id}", json=update_data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

# Test deleting an item
print("\nDeleting an item...")
response = requests.delete(f"{base_url}/items/{item_id}")
print(f"Status Code: {response.status_code}")

# Verify item is deleted
print("\nVerifying item is deleted...")
response = requests.get(f"{base_url}/items/{item_id}")
print(f"Status Code: {response.status_code}")
print("Item successfully deleted!" if response.status_code == 404 else "Item still exists")