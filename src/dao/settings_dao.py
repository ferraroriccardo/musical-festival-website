import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(BASE_DIR, 'musical_festival.db')


def get_staff_passw():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()

        query = "SELECT staff_password FROM SETTINGS;"
        cursor.execute(query)

        password = cursor.fetchone()
        if password is None:
            return False, "DATABASE_ERROR_GET_STAFF_PASSW"
        return password[0]
    except Exception as e:
        return False, "DATABASE_ERROR_GET_STAFF_PASSW"
    finally:
        cursor.close()
        conn.close()


def set_staff_passw(plain_text_passw):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM SETTINGS")

        query = "INSERT INTO SETTINGS (staff_password) VALUES (?);"
        hashed_passw = generate_password_hash(plain_text_passw)
        cursor.execute(query, (hashed_passw, ))

        conn.commit()
        return
    except Exception as e:
        return False, "DATABASE_ERROR_SET_STAFF_PASSW"
    finally:
        cursor.close()
        conn.close()

def time_to_minutes(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 60 + m