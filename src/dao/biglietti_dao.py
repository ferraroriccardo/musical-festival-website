import sqlite3
from .settings_dao import DB_PATH

def buy_ticket_for_user(user_id, ticket_type, start_day):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        already_bought = has_ticket(user_id, conn)
        if isinstance(already_bought, tuple) and already_bought[0] is False:
            return already_bought
        if already_bought:
            return False, "HAS_TICKET"

        remaining = get_remaining_tickets(ticket_type, conn)
        if remaining == 0:
            return False, "NO_TICKETS_AVAILABLE"
        
        insert_query = "INSERT INTO BIGLIETTI (tipo, giorno_inizio, id_utente) VALUES (?, ?, ?);"
        cur = conn.execute(insert_query, (ticket_type, start_day, user_id))
        ticket_id = cur.lastrowid
        
        update_query = "UPDATE UTENTI SET id_biglietto = ? WHERE id = ?;"
        conn.execute(update_query, (ticket_id, user_id))
        conn.commit()
        return True, None
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return False, "DATABASE_ERROR_BUY_TICKET_FOR_USER"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def has_ticket(user_id, conn):
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM BIGLIETTI WHERE id_utente = ?;"
        cur = conn.execute(query, (user_id, ))
        ticket = cur.fetchone()
        return bool(ticket)
    except Exception as e:
        return False, "DATABASE_ERROR_GET_REMAINING_TICKETS"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    

def get_remaining_tickets(ticket_type, conn):
    try:
        query = "SELECT COUNT(id) FROM BIGLIETTI WHERE tipo = ?;"
        cur = conn.execute(query, (ticket_type, ))
        count = cur.fetchone()[0]
        return 200 - count
    except Exception as e:
        return False, "DATABASE_ERROR_GET_REMAINING_TICKETS"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_ticket_by_user_id(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM BIGLIETTI WHERE id_utente = ?"
        cursor.execute(query, (user_id, ))
        ticket = cursor.fetchone()

        return ticket
    except Exception as e:
        return False, "DATABASE_ERROR_GET_TICKET_BY_USER_ID"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_sells():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT tipo, COUNT(id) as count FROM BIGLIETTI GROUP BY tipo;"
        cursor.execute(query)
        tickets = cursor.fetchall()

        return tickets
    except Exception as e:
        return False, "DATABASE_ERROR_GET_SELLS"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()