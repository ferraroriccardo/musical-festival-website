import sqlite3

def get_shows():
    conn = sqlite3.connect('musical_festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM SPETTACOLI;"
    cursor.execute(query)

    shows = cursor.fetchall()
    conn.close()
    return shows

def create_event(conn, day, hour_slot, artist, description, genre, published, stage):
    try:
        overlapping = get_overlapping_published_shows(day, hour_slot, conn)
        if overlapping:
            return False, "SHOW_SLOT_ALREADY_OCCUPIED"
        
        insert_query = "INSERT INTO SPETTACOLI (day, hour_slot, artist, description, genre, published, stage) VALUES (?, ?, ?, ?, ?, ?, ?);"
        conn.execute(insert_query, (day, hour_slot, artist, description, genre, published, stage))
        return True, None
    
    except Exception as e:
        conn.rollback()
        return False, "DATABASE_ERROR"

def get_overlapping_published_shows(day, hour_slot, conn):
    cursor = conn.cursor()

    query = "SELECT * FROM SPETTACOLI WHERE giorno = ? AND slot_orario = ? AND pubblicato = 'True';"
    cursor.execute(query, (day, hour_slot))

    shows = cursor.fetchall()
    return shows