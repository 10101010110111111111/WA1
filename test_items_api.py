import unittest
import json
from app_api import app, db, ItemModel

class ItemsAPITestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and test database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Add a test item
            item = ItemModel(
                title="Test Item",
                description="Test Description",
                done=False
            )
            db.session.add(item)
            db.session.commit()
            self.test_item_id = item.id

    def tearDown(self):
        """Clean up test database"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_all_items(self):
        """Test GET /items endpoint"""
        with app.app_context():
            response = self.app.get('/items')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['title'], 'Test Item')

    def test_get_item_by_id(self):
        """Test GET /items/{id} endpoint"""
        with app.app_context():
            response = self.app.get(f'/items/{self.test_item_id}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['title'], 'Test Item')
            self.assertEqual(data['description'], 'Test Description')
            self.assertEqual(data['done'], False)

    def test_get_item_not_found(self):
        """Test GET /items/{id} endpoint with non-existent item"""
        with app.app_context():
            response = self.app.get('/items/999')
            self.assertEqual(response.status_code, 404)

    def test_create_item(self):
        """Test POST /items endpoint"""
        with app.app_context():
            new_item = {
                'title': 'New Test Item',
                'description': 'New Test Description',
                'done': True
            }
            response = self.app.post('/items',
                                   data=json.dumps(new_item),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            self.assertEqual(data['title'], 'New Test Item')
            self.assertEqual(data['description'], 'New Test Description')
            self.assertEqual(data['done'], True)
            self.assertIn('id', data)
            self.assertIn('created_at', data)

    def test_create_item_missing_title(self):
        """Test POST /items endpoint with missing title"""
        with app.app_context():
            new_item = {
                'description': 'New Test Description',
                'done': True
            }
            response = self.app.post('/items',
                                   data=json.dumps(new_item),
                                   content_type='application/json')
            self.assertEqual(response.status_code, 400)

    def test_update_item(self):
        """Test PUT /items/{id} endpoint"""
        with app.app_context():
            updated_item = {
                'title': 'Updated Test Item',
                'description': 'Updated Test Description',
                'done': True
            }
            response = self.app.put(f'/items/{self.test_item_id}',
                                  data=json.dumps(updated_item),
                                  content_type='application/json')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['title'], 'Updated Test Item')
            self.assertEqual(data['description'], 'Updated Test Description')
            self.assertEqual(data['done'], True)

    def test_update_item_not_found(self):
        """Test PUT /items/{id} endpoint with non-existent item"""
        with app.app_context():
            updated_item = {
                'title': 'Updated Test Item',
                'description': 'Updated Test Description',
                'done': True
            }
            response = self.app.put('/items/999',
                                  data=json.dumps(updated_item),
                                  content_type='application/json')
            self.assertEqual(response.status_code, 404)

    def test_delete_item(self):
        """Test DELETE /items/{id} endpoint"""
        with app.app_context():
            response = self.app.delete(f'/items/{self.test_item_id}')
            self.assertEqual(response.status_code, 204)
            
            # Verify item is deleted
            response = self.app.get(f'/items/{self.test_item_id}')
            self.assertEqual(response.status_code, 404)

    def test_delete_item_not_found(self):
        """Test DELETE /items/{id} endpoint with non-existent item"""
        with app.app_context():
            response = self.app.delete('/items/999')
            self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()