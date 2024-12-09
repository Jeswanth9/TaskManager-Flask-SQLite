from flask import Flask, jsonify, request, render_template
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory list to store tasks
tasks = []

# Serve the frontend
@app.route('/')
def home():
    logger.info('Rendered HTML page')
    return render_template('index.html')


@app.route('/tasks', methods=['POST'])
def add_task():
    logger.info('Received request for /tasks POST method - used to add new task')
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400
    # Create a new task with a unique ID
    new_task = {
        'id': len(tasks) + 1,  # Auto-increment ID based on the list length
        'name': data['name'],
        'description': data.get('description', '')
    }
    tasks.append(new_task)  # Add the task to the in-memory list
    logger.info('Completed request for /tasks POST method - used to add new task')
    return jsonify(new_task), 201  # Return the new task


# View all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    logger.info('Received request for /tasks GET method - used to fetch all tasks')
    logger.info('Completed request for /tasks GET method - fetched all tasks')
    return jsonify(tasks)

# Update an existing task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    logger.info('Received request for /tasks PUT method - used to update a task')
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400

    for task in tasks:
        if task['id'] == task_id:
            task['name'] = data['name']
            task['description'] = data.get('description', '')
            logger.info(f'Updated task: {task}')
            return jsonify({'message': 'Task updated'})

    logger.error(f'Task with ID {task_id} not found')
    return jsonify({'error': 'Task not found'}), 404


# Delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    logger.info('Received request for /tasks DELETE method - used to delete a task')
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    logger.info('Completed request for /tasks DELETE method - task deleted')
    return jsonify({'message': f'Task with id {task_id} deleted'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8055)
