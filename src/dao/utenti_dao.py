import sqlite3

from flask import flash
from .settings_dao import DB_PATH

def get_user_by_id(user_id):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM UTENTI WHERE id = ?;"
        cursor.execute(query, (user_id, ))

        user = cursor.fetchone()
        return dict(user)
    except Exception as e:
        return False, "DATABASE_ERROR_GET_USER_BY_ID"
    finally:
        cursor.close()
        conn.close()

def get_user_by_email(email):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM UTENTI WHERE email = ?;"
        cursor.execute(query, (email, ))

        user = cursor.fetchone()
        return user
    except Exception as e:
        return None
    finally:
        cursor.close()
        conn.close()

def create_user(email, password, type):
    try:
        conn = sqlite3.connect(DB_PAT, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "INSERT INTO UTENTI (email, password, tipo) VALUES (?, ?, ?);"
        cursor.execute(query, (email, password, type))
        conn.commit()

        query = "SELECT * FROM UTENTI WHERE email = ?;"
        cursor.execute(query, (email, ))

        user = cursor.fetchone()
        return user
        
    except Exception as e:
        return False, "DATABASE_ERROR_CREATE_USER"
    finally:
        cursor.close()
        conn.close()
