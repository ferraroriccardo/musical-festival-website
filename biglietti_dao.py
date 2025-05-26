import sqlite3

def buy_ticket_for_user(user_id, ticket_type):
    conn = sqlite3.connect("musical_festival.db")
    try:
        with conn:
            remaining = get_remaining_tickets(ticket_type, conn)
            if remaining == 0:
                return False, "NO_TICKETS_AVAILABLE"
            # esegui acquisto
            # ... (insert/update query)
            # esempio: conn.execute("UPDATE ...")
            query = "INSERT INTO BIGLIETTI VALUES (?, ?, ?)"
            conn.execute(query, (user_id, ))
        return True, None
    except Exception as e:
        conn.rollback()
        return False, "DATABASE_ERROR"
    finally:
        conn.close()

def get_remaining_tickets(ticket_tipe, conn):
    query = "SELECT COUNT(id) FROM BIGLIETTI WHERE tipo = (ticket_type) (?)"
    conn.execute(query, (ticket_tipe, ))
    return 200 - conn.fetchone()
