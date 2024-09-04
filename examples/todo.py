from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
import sqlite3

app = Flask(__name__)
api = Api(app)

with sqlite3.connect('todo.db') as conn:
    conn.row_factory = sqlite3.Row  # Access columns by names

    def get_db_connection():
        return sqlite3.connect('todo.db')

    def abort_if_todo_doesnt_exist(todo_id):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
            todo = cursor.fetchone()
            if todo is None:
                abort(404, message="Todo {} doesn't exist".format(todo_id))

    parser = reqparse.RequestParser()
    parser.add_argument('task')

    class Todo(Resource):
        def get(self, todo_id):
            abort_if_todo_doesnt_exist(todo_id)
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
                todo = cursor.fetchone()
                return dict(todo)

        def delete(self, todo_id):
            abort_if_todo_doesnt_exist(todo_id)
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
                conn.commit()
                return '', 204

        def put(self, todo_id):
            args = parser.parse_args()
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE todos SET task = ? WHERE id = ?", (args['task'], todo_id))
                conn.commit()
                return {'id': todo_id, 'task': args['task']}, 201

    class TodoList(Resource):
        def get(self):
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM todos")
                todos = cursor.fetchall()
                return [dict(todo) for todo in todos]

        def post(self):
            args = parser.parse_args()
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO todos (task) VALUES (?)", (args['task'],))
                todo_id = cursor.lastrowid
                conn.commit()
                return {'id': todo_id, 'task': args['task']}, 201

    class BatchTodoUpdate(Resource):
        def put(self):
            update_ids = request.json.get('update_ids', [])
            if not all(isinstance(id, int) for id in update_ids):
                abort(400, message="All IDs must be integers.")
            task_description = request.json.get('task', '')
            with get_db_connection() as conn:
                cursor = conn.cursor()
                for todo_id in update_ids:
                    cursor.execute("UPDATE todos SET task = ? WHERE id = ?", (task_description, todo_id))
                conn.commit()
                return f"Updated {len(update_ids)} tasks", 200

api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')
api.add_resource(BatchTodoUpdate, '/todos/batch_update')

if __name__ == '__main__':
    app.run(debug=True)
