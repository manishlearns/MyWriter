import sqlite3
from datetime import datetime
import os

DB_NAME = "scheduler.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_text TEXT NOT NULL,
            image_url TEXT,
            scheduled_time TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            error_msg TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_post(draft_text, scheduled_time, image_url=None):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO scheduled_posts (draft_text, scheduled_time, image_url, status)
            VALUES (?, ?, ?, 'PENDING')
        ''', (draft_text, scheduled_time, image_url))
        conn.commit()
        return c.lastrowid
    except Exception as e:
        print(f"Error adding post to DB: {e}")
        return None
    finally:
        conn.close()

def get_due_posts():
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    # Find pending posts where scheduled_time <= now
    c.execute('''
        SELECT * FROM scheduled_posts 
        WHERE status = 'PENDING' AND scheduled_time <= ?
    ''', (now,))
    posts = c.fetchall()
    conn.close()
    return posts

def update_post_status(post_id, status, error_msg=None):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        UPDATE scheduled_posts 
        SET status = ?, error_msg = ?
        WHERE id = ?
    ''', (status, error_msg, post_id))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
