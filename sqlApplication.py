from flask import Flask, jsonify, request, render_template
import mysql.connector
import logging
import boto3
from botocore.config import Config
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CloudWatch Logs client (optional, but good practice for cloud deployments)
cw_logs = boto3.client('logs', config=Config(region_name='eu-north-1'))  # Ensure correct region
log_group_name = 'TaskManager-Flask-MySQL-Logs'  # Updated log group name
log_stream_name = 'flask-app-logs'

app = Flask(__name__)

# Database connection details (best practice: store these securely, e.g., environment variables)
DB_HOST = "database-1.c764sga4wv30.eu-north-1.rds.amazonaws.com"
DB_PORT = 3306
DB_USER = "admin"
DB_PASSWORD = "kanban123"
DB_NAME = "taskdb"


# Helper function for database interaction
def query_db(query, args=(), one=False):
    try:
        mydb = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cur = mydb.cursor(dictionary=True) # Returns data as dictionaries
        cur.execute(query, args)
        rv = cur.fetchall()
        mydb.commit()  # Important for insert/update/delete operations
        cur.close()
        mydb.close()
        return (rv[0] if rv else None) if one else rv
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}")
        return None # or raise the exception depending on your error handling strategy



# Frontend route
@app.route('/')
def home():
    logger.info('Rendered HTML page')
    return render_template('index.html')


# API routes (add, get, update, delete tasks)
@app.route('/tasks', methods=['POST'])
def add_task():
    logger.info('Received request for /tasks POST method')
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400

    result = query_db("INSERT INTO tasks (name, description) VALUES (%s, %s)", (data['name'], data.get('description', '')))
    if result:
        logger.info('Completed request for /tasks POST method')
        return jsonify({'message': 'Task added'}), 201
    else:
        return jsonify({'error': 'Failed to add task'}), 500 # Internal Server Error on DB failure


@app.route('/tasks', methods=['GET'])
def get_tasks():
    logger.info('Received request for /tasks GET method')
    tasks = query_db('SELECT * FROM tasks')
    if tasks:
        logger.info('Completed request for /tasks GET method')
        return jsonify(tasks)
    else:
        return jsonify({'error': 'Failed to fetch tasks'}), 500


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    logger.info('Received request for /tasks PUT method')
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400

    result = query_db("UPDATE tasks SET name = %s, description = %s WHERE id = %s", (data['name'], data.get('description', ''), task_id))

    if result:
        logger.info('Completed request for /tasks PUT method')
        return jsonify({'message': 'Task updated'})
    else:
        return jsonify({'error': 'Task not found or update failed'}), 404 # Not Found or DB error


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    logger.info('Received request for /tasks DELETE method')
    result = query_db('DELETE FROM tasks WHERE id = %s', (task_id,))
    if result:
        logger.info('Completed request for /tasks DELETE method')
        return jsonify({'message': f'Task with id {task_id} deleted'})
    else:
        return jsonify({'error': 'Task not found or delete failed'}), 404



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8055)

