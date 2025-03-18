import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = 'todo.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())

@app.route("/")
def index():
    try:
        with get_db_connection() as conn:
            tasks = conn.execute('SELECT * FROM tasks').fetchall()
        return render_template("index.html", tasks=tasks)
    except sqlite3.Error as e:
        print(f"Error fetching tasks from database: {e}")
        return "Database error", 500

@app.route("/add", methods=["POST"])
def add_task():
    task_content = request.form.get("task")
    if task_content:
        try:
            with get_db_connection() as conn:
                conn.execute('INSERT INTO tasks (content, completed) VALUES (?, ?)', (task_content, False))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding task: {e}")
            return "Database error", 500
    return redirect(url_for("index"))

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    try:
        with get_db_connection() as conn:
            conn.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
            conn.commit()
        return redirect(url_for("index"))
    except sqlite3.Error as e:
        print(f"Error completing task {task_id}: {e}")
        return "Database error", 500

@app.route("/undo/<int:task_id>")
def undo_task(task_id):
    try:
        with get_db_connection() as conn:
            conn.execute('UPDATE tasks SET completed = 0 WHERE id = ?', (task_id,))
            conn.commit()
        return redirect(url_for("index"))
    except sqlite3.Error as e:
        print(f"Error undoing task {task_id}: {e}")
        return "Database error", 500

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    try:
        with get_db_connection() as conn:
            conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
        return redirect(url_for("index"))
    except sqlite3.Error as e:
        print(f"Error deleting task {task_id}: {e}")
        return "Database error", 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

