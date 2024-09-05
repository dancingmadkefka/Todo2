import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name: str = "todo.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        self.connect()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                priority TEXT,
                completed INTEGER DEFAULT 0,
                category TEXT DEFAULT "Other"
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id),
                PRIMARY KEY (task_id, tag_id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE
            )
        ''')
                            
        self.conn.commit()
        self.disconnect()

    def add_task(self, title: str, description: str = "", due_date: str = "", priority: str = "Med", category: str = "Other") -> int:
        self.connect()
        self.cursor.execute('''
            INSERT INTO tasks (title, description, due_date, priority, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, due_date, priority, category))
        task_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return task_id

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        self.connect()
        self.cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task_data = self.cursor.fetchone()
        if task_data:
            return {
                'id': task_data[0],
                'title': task_data[1],
                'description': task_data[2],
                'due_date': task_data[3],
                'priority': task_data[4],
                'completed': bool(task_data[5]),
                'category': task_data[6]
            }
        return None

    def update_task(self, task_id: int, title: str, completed: bool, due_date: str, priority: str, category: str, description: str = ""):
        self.connect()
        try:
            self.cursor.execute('''
                UPDATE tasks
                SET title = ?, description = ?, due_date = ?, priority = ?, completed = ?, category = ?
                WHERE id = ?
            ''', (title, description, due_date, priority, int(completed), category, task_id))
            self.conn.commit()
            print(f"Task {task_id} updated in database: completed = {completed}")
        except Exception as e:
            print(f"Error updating task in database: {str(e)}")
        finally:
            self.disconnect()

    def delete_task(self, task_id: int):
        self.connect()
        self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        self.disconnect()

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        self.connect()
        self.cursor.execute('SELECT * FROM tasks')
        tasks = self.cursor.fetchall()
        self.disconnect()
        return [{
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'due_date': task[3],
            'priority': task[4],
            'completed': bool(task[5]),
            'category': task[6]
        } for task in tasks]
    
    def get_all_tags(self):
        self.connect()
        self.cursor.execute('SELECT DISTINCT name FROM tags')
        tags = [row[0] for row in self.cursor.fetchall()]
        self.disconnect()
        return tags

    def add_tag(self, name: str) -> int:
        self.connect()
        self.cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (name,))
        tag_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return tag_id

    def add_tag_to_task(self, task_id: int, tag_name: str):
        tag_id = self.add_tag(tag_name)
        self.connect()
        self.cursor.execute('INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)', (task_id, tag_id))
        self.conn.commit()
        self.disconnect()

    def get_task_tags(self, task_id: int) -> List[str]:
        self.connect()
        self.cursor.execute('''
            SELECT tags.name
            FROM tags
            JOIN task_tags ON tags.id = task_tags.tag_id
            WHERE task_tags.task_id = ?
        ''', (task_id,))
        tags = [row[0] for row in self.cursor.fetchall()]
        self.disconnect()
        return tags

    def remove_tag_from_task(self, task_id: int, tag_name: str):
        self.connect()
        self.cursor.execute('''
            DELETE FROM task_tags
            WHERE task_id = ? AND tag_id = (SELECT id FROM tags WHERE name = ?)
        ''', (task_id, tag_name))
        self.conn.commit()
        self.disconnect()

    def add_category(self, name: str):
        self.connect()
        self.cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (name,))
        self.conn.commit()
        self.disconnect()

    def get_all_categories(self) -> List[str]:
        self.connect()
        self.cursor.execute('SELECT name FROM categories')
        categories = [row[0] for row in self.cursor.fetchall()]
        self.disconnect()
        return categories

    def delete_category(self, name: str):
        self.connect()
        try:
            # Delete the category from the categories table
            self.cursor.execute('DELETE FROM categories WHERE name = ?', (name,))
            
            # Update tasks with the deleted category to use "Other" category
            self.cursor.execute('UPDATE tasks SET category = "Other" WHERE category = ?', (name,))
            
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting category: {str(e)}")
            self.conn.rollback()
        finally:
            self.disconnect()