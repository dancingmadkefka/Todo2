import sqlite3
import logging
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_name: str = "todo.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        self.connect()
        try:
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
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def add_task(self, title: str, description: str = "", due_date: str = "", priority: str = "Med", category: str = "Other") -> int:
        self.connect()
        try:
            self.cursor.execute('''
                INSERT INTO tasks (title, description, due_date, priority, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, due_date, priority, category))
            task_id = self.cursor.lastrowid
            self.conn.commit()
            return task_id
        except sqlite3.Error as e:
            logging.error(f"Error adding task: {e}")
            self.conn.rollback()
            return -1
        finally:
            self.disconnect()

    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            task = self.cursor.fetchone()
            if task:
                return {
                    'id': task[0],
                    'title': task[1],
                    'description': task[2],
                    'due_date': task[3],
                    'priority': task[4],
                    'completed': bool(task[5]),
                    'category': task[6]
                }
            return None
        except sqlite3.Error as e:
            logging.error(f"Error getting task: {e}")
            return None
        finally:
            self.disconnect()

    def update_task(self, task_id: int, title: str, completed: bool, due_date: str, priority: str, category: str, description: str = ""):
        self.connect()
        try:
            self.cursor.execute('''
                UPDATE tasks
                SET title = ?, description = ?, due_date = ?, priority = ?, completed = ?, category = ?
                WHERE id = ?
            ''', (title, description, due_date, priority, int(completed), category, task_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error updating task: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def delete_task(self, task_id: int):
        self.connect()
        try:
            self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error deleting task: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        self.connect()
        try:
            self.cursor.execute('SELECT * FROM tasks')
            tasks = self.cursor.fetchall()
            return [{
                'id': task[0],
                'title': task[1],
                'description': task[2],
                'due_date': task[3],
                'priority': task[4],
                'completed': bool(task[5]),
                'category': task[6]
            } for task in tasks]
        except sqlite3.Error as e:
            logging.error(f"Error getting all tasks: {e}")
            return []
        finally:
            self.disconnect()

    def add_category(self, name: str):
        self.connect()
        try:
            self.cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (name,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding category: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def get_all_categories(self) -> List[str]:
        self.connect()
        try:
            self.cursor.execute('SELECT name FROM categories')
            categories = [row[0] for row in self.cursor.fetchall()]
            return categories
        except sqlite3.Error as e:
            logging.error(f"Error getting categories: {e}")
            return []
        finally:
            self.disconnect()

    def delete_category(self, name: str):
        self.connect()
        try:
            self.cursor.execute('DELETE FROM categories WHERE name = ?', (name,))
            self.cursor.execute('UPDATE tasks SET category = "Other" WHERE category = ?', (name,))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error deleting category: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def set_setting(self, key: str, value: str):
        self.connect()
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            ''', (key, value))
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting setting: {e}")
            self.conn.rollback()
        finally:
            self.disconnect()

    def get_setting(self, key: str, default: str = "") -> str:
        self.connect()
        try:
            self.cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = self.cursor.fetchone()
            return result[0] if result else default
        except sqlite3.Error as e:
            logging.error(f"Error getting setting: {e}")
            return default
        finally:
            self.disconnect()

    def get_date_format(self) -> str:
        return self.get_setting("date_format", "%Y-%m-%d")

    def set_date_format(self, date_format: str):
        self.set_setting("date_format", date_format)