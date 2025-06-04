import sqlite3

from flask_login import current_user

def buy_ticket_for_user(user_id, ticket_type, start_day, conn):
    try:
        remaining = get_remaining_tickets(ticket_type, conn)
        if remaining == 0:
            return False, "NO_TICKETS_AVAILABLE"
        
        insert_query = "INSERT INTO BIGLIETTI (tipo, giorno_inizio, id_utente) VALUES (?, ?, ?);"
        cur = conn.execute(insert_query, (ticket_type, start_day, user_id))
        ticket_id = cur.lastrowid
        
        update_query = "UPDATE UTENTI SET id_biglietto = ? WHERE id = ?;"
        conn.execute(update_query, (ticket_id, user_id))
        return True, None
    except Exception as e:
        return False, "DATABASE_ERROR_BUY_TICKET_FOR_USER"

def get_remaining_tickets(ticket_type, conn):
    try:
        query = "SELECT COUNT(id) FROM BIGLIETTI WHERE tipo = ?;"
        cur = conn.execute(query, (ticket_type, ))
        count = cur.fetchone()[0]
        return 200 - count
    except Exception as e:
        return False, "DATABASE_ERROR_GET_REMAINING_TICKETS"

def get_ticket_by_user_id(current_user_id):
    conn = sqlite3.connect("/musical-festival-website/musical_festival.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM BIGLIETTI WHERE id_utente = ?"
        cursor.execute(query, (current_user_id, ))
        ticket = cursor.fetchone()
        conn.close()
        return ticket
    except Exception as e:
        return False, "DATABASE_ERROR_GET_TICKET_BY_USER_ID"