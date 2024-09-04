from flask_testing import TestCase
from examples.todo import app, api
from unittest.mock import patch, MagicMock
import unittest
import json


class TestTodoAPI(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    @patch('examples.todo.get_db_connection')
    def test_get_all_todos(self, mock_db):
        mock_db.return_value.cursor.return_value.fetchall.return_value = [
            {'id': 1, 'task': 'Test Task 1'},
            {'id': 2, 'task': 'Test Task 2'}
        ]
        response = self.client.get('/todos')
        self.assert200(response)
        self.assertEqual(len(response.json), 2)

    @patch('examples.todo.get_db_connection')
    def test_post_todo(self, mock_db):
        mock_connection = MagicMock()
        mock_connection.cursor.return_value.lastrowid = 1
        mock_db.return_value = mock_connection
        response = self.client.post('/todos', json={'task': 'New Task'})
        self.assertStatus(response, 201)
        self.assertEqual(response.json, {'id': 1, 'task': 'New Task'})

    @patch('examples.todo.get_db_connection')
    def test_get_specific_todo(self, mock_db):
        mock_db.return_value.cursor.return_value.fetchone.return_value = {'id': 1, 'task': 'Test Task'}
        response = self.client.get('/todos/1')
        self.assert200(response)
        self.assertEqual(response.json, {'id': 1, 'task': 'Test Task'})

    @patch('examples.todo.get_db_connection')
    def test_put_specific_todo(self, mock_db):
        mock_db.return_value.cursor.return_value.rowcount = 1
        response = self.client.put('/todos/1', json={'task': 'Updated Task'})
        self.assertStatus(response, 200)
        self.assertEqual(response.json, {'id': '1', 'task': 'Updated Task'})

    @patch('examples.todo.get_db_connection')
    def test_delete_specific_todo(self, mock_db):
        mock_db.return_value.cursor.return_value.rowcount = 1
        response = self.client.delete('/todos/1')
        self.assertStatus(response, 204)

    @patch('examples.todo.get_db_connection')
    def test_put_batch_update(self, mock_db):
        mock_db.return_value.cursor.return_value.rowcount = 2
        response = self.client.put('/todos/batch_update', json={'update_ids': [1, 2], 'task': 'Batch Updated Task'})
        self.assert200(response)
        self.assertIn('Updated 2 tasks', response.get_data(as_text=True))

    @patch('examples.todo.get_db_connection')
    def test_get_todo_not_found(self, mock_db):
        mock_db.return_value.cursor.return_value.fetchone.return_value = None
        response = self.client.get('/todos/99')
        self.assert404(response)

    @patch('examples.todo.get_db_connection')
    def test_put_todo_not_found(self, mock_db):
        mock_db.return_value.cursor.return_value.rowcount = 0
        response = self.client.put('/todos/99', json={'task': 'Nonexistent Task'})
        self.assert404(response)

    @patch('examples.todo.get_db_connection')
    def test_delete_todo_not_found(self, mock_db):
        mock_db.return_value.cursor.return_value.rowcount = 0
        response = self.client.delete('/todos/99')
        self.assert404(response)

    @patch('examples.todo.get_db_connection')
    def test_put_batch_update_invalid_id(self, mock_db):
        response = self.client.put('/todos/batch_update', json={'update_ids': ['a', 2], 'task': 'Invalid ID Task'})
        self.assert400(response)


if __name__ == '__main__':
    unittest.main()

