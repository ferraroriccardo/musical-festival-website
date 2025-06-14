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
        if user is None:
            return None
        return dict(user)
    except Exception as e:
        return False, "DATABASE_ERROR_GET_USER_BY_ID"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def get_user_by_email(email):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM UTENTI WHERE email = ?;"
        cursor.execute(query, (email, ))

        user = cursor.fetchone()
        if user is None:
            return None
        return dict(user)
    except Exception as e:
        return False, "DATABASE_ERROR_GET_USER_BY_EMAIL"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def create_user(name, email, password, user_type):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "INSERT INTO UTENTI (nome, email, password, tipo) VALUES (?, ?, ?, ?);"
        cursor.execute(query, (name, email, password, user_type))
        conn.commit()

        query = "SELECT * FROM UTENTI WHERE email = ?;"
        cursor.execute(query, (email, ))

        user = cursor.fetchone()
        return user
        
    except Exception as e:
        return False, "DATABASE_ERROR_CREATE_USER"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
