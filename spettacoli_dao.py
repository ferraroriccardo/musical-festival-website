import sqlite3
import palchi_dao

def get_shows():
    conn = sqlite3.connect('musical_festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT artista FROM SPETTACOLI;"
    cursor.execute(query)

    shows = cursor.fetchall()
    conn.close()
    return shows

def create_event(conn, day, hour_slot, artist, description, genre, published, stage_name):
    try:
        overlapping = get_overlapping_published_shows(day, hour_slot, conn)
        if overlapping:
            return False, "SHOW_SLOT_ALREADY_OCCUPIED"
        
        artist_already_performing = is_already_performing(artist)
        if artist_already_performing:
            return False, "ARTIST_ALREADY_PERFORMING"
        
        stage_id = palchi_dao.get_palco_by_name(stage_name)
        
        insert_query = "INSERT INTO SPETTACOLI (day, hour_slot, artist, description, genre, published, stage_id) VALUES (?, ?, ?, ?, ?, ?, ?);"
        conn.execute(insert_query, (day, hour_slot, artist, description, genre, published, stage_id))
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

def is_already_performing(artist):
    conn = sqlite3.connect('musical_festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT artista FROM SPETTACOLI WHERE artista = ?;"
    cursor.execute(query, (artist, ))

    shows = cursor.fetchone()
    conn.close()
    if shows:
        return True
    return False
    
