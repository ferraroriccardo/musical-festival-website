import sqlite3
from werkzeug.security import generate_password_hash

def get_staff_passw():
    conn = sqlite3.connect("musical_festival.db")
    cursor = conn.cursor()

    query = "SELECT staff_password FROM STATIC"
    cursor.execute(query)

    user = cursor.fetchone()
    conn.close()
    return user

def set_staff_passw(plain_text_passw):
    conn = sqlite3.connect("musical_festival.db")
    cursor = conn.cursor()

    # Svuota la tabella STATIC prima di inserire la nuova password
    cursor.execute("DELETE FROM STATIC")

    query = "INSERT INTO STATIC (staff_password) VALUES (?)"
    hashed_passw = generate_password_hash(plain_text_passw)
    cursor.execute(query, (hashed_passw, ))

    conn.commit()
    conn.close()
    return