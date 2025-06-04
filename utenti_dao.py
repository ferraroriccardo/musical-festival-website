import sqlite3

def get_user_by_id(user_id):
    try:
        conn = sqlite3.connect("musical_festival.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM UTENTI WHERE id = ?;"
        cursor.execute(query, (user_id, ))

        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        return False, "DATABASE_ERROR_GET_USER_BY_ID"

def get_user_by_email(email):
    try:
        conn = sqlite3.connect("musical_festival.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM UTENTI WHERE email = ?;"
        cursor.execute(query, (email, ))

        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        return False, "DATABASE_ERROR_GET_USER_BY_EMAIL"

def create_user(email, password, type):
    try:
        conn = sqlite3.connect("musical_festival.db")
        cursor = conn.cursor()

        query = "INSERT INTO UTENTI (email, password, tipo) VALUES (?, ?, ?);"
        cursor.execute(query, (email, password, type))
        conn.commit()
        
        conn.close()
        return True
    except Exception as e:
        return False, "DATABASE_ERROR_CREATE_USER"