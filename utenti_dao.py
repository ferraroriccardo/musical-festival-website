import sqlite3

def get_user_by_id(user_id):
    conn = sqlite3.connect("musical_festival.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM UTENTI WHERE id = ?"
    cursor.execute(query, (user_id, ))

    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = sqlite3.connect("musical_festival.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM UTENTI WHERE id = ?"
    cursor.execute(query, (email, ))

    user = cursor.fetchone()
    conn.close()
    return user