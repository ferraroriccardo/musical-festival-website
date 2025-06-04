import sqlite3
from werkzeug.security import generate_password_hash

def get_staff_passw():
    try:
        conn = sqlite3.connect("musical_festival.db")
        cursor = conn.cursor()

        query = "SELECT staff_password FROM SETTINGS;"
        cursor.execute(query)

        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        return False, "DATABASE_ERROR_GET_STAFF_PASSW"

def set_staff_passw(plain_text_passw):
    try:
        conn = sqlite3.connect("musical_festival.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM SETTINGS")

        query = "INSERT INTO SETTINGS (staff_password) VALUES (?);"
        hashed_passw = generate_password_hash(plain_text_passw)
        cursor.execute(query, (hashed_passw, ))

        conn.commit()
        conn.close()
        return
    except Exception as e:
        return False, "DATABASE_ERROR_SET_STAFF_PASSW"

def get_connection():
    try:
        conn = sqlite3.connect("musical_festival.db")
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        return False, "DATABASE_ERROR_GET_CONNECTION"