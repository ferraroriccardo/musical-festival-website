import sqlite3
from werkzeug.security import generate_password_hash

def get_staff_passw():
    conn = sqlite3.connect("musical-festival-website/musical_festival.db")
    cursor = conn.cursor()

    query = "SELECT staff_password FROM SETTINGS;"
    cursor.execute(query)

    user = cursor.fetchone()
    conn.close()
    return user

def set_staff_passw(plain_text_passw):
    conn = sqlite3.connect("musical-festival-website/musical_festival.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM SETTINGS")

    query = "INSERT INTO SETTINGS (staff_password) VALUES (?);"
    hashed_passw = generate_password_hash(plain_text_passw)
    cursor.execute(query, (hashed_passw, ))

    conn.commit()
    conn.close()
    return

def get_connection():
    conn = sqlite3.connect("musical-festival-website/musical_festival.db")
    conn.row_factory = sqlite3.Row
    return conn