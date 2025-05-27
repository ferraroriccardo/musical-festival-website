import sqlite3

def buy_ticket_for_user(user_id, ticket_type, start_day, conn):
    try:
        remaining = get_remaining_tickets(ticket_type, conn)
        if remaining == 0:
            return False, "NO_TICKETS_AVAILABLE"
        
        insert_query = "INSERT INTO BIGLIETTI (user_id, tipo, start_day) VALUES (?, ?, ?);"
        cur = conn.execute(insert_query, (user_id, ticket_type, start_day))
        ticket_id = cur.lastrowid
        
        update_query = "UPDATE UTENTI SET id_biglietto = ? WHERE id = ?;"
        conn.execute(update_query, (ticket_id, user_id))
        return True, None
    except Exception as e:
        conn.rollback()
        return False, "DATABASE_ERROR"

def get_remaining_tickets(ticket_type, conn):
    query = "SELECT COUNT(id) FROM BIGLIETTI WHERE tipo = ?;"
    cur = conn.execute(query, (ticket_type, ))
    count = cur.fetchone()[0]
    return 200 - count

def get_ticket_by_user_id(current_user_id):
    conn = sqlite3.connect("musical_festival.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM BIGLIETTI WHERE user_id = ?"
    cursor.execute(query, (current_user_id, ))
    ticket = cursor.fetchone()

    conn.close()
    return ticket