import sqlite3
import palchi_dao

def get_shows():
    try:
        conn = sqlite3.connect('/musical-festival-website/musical_festival.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM SPETTACOLI;"
        cursor.execute(query)

        shows = cursor.fetchall()
        conn.close()
        return shows
    except Exception as e:
        return False, "DATABASE_ERROR_GET_SHOWS"

def get_shows_filtered(giorno, palco, genere):
    try:
        conn = sqlite3.connect('/musical-festival-website/musical_festival.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT artista FROM SPETTACOLI WHERE 1=1"
        params = []
        if giorno:
            query += " AND giorno = ?"
            params.append(giorno)
        if palco:
            query += " AND palco = ?"
            params.append(palco)
        if genere:
            query += " AND genere = ?"
            params.append(genere)

        cursor.execute(query, params)
        shows = cursor.fetchall()
        conn.close()
        return shows
    except Exception as e:
        return False, "DATABASE_ERROR_GET_SHOWS_FILTERED"

def create_event(conn, day, start_hour, duration, artist, description, genre, published, stage_name):
    try:
        overlapping = get_overlapping_published_shows(day, start_hour, duration, conn)
        if overlapping:
            return False, "SHOW_SLOT_ALREADY_OCCUPIED"
        
        artist_already_performing = is_already_performing(artist)
        if artist_already_performing:
            return False, "ARTIST_ALREADY_PERFORMING"
        
        stage_id = palchi_dao.get_palco_by_name(stage_name)
        
        insert_query = "INSERT INTO SPETTACOLI (giorno, ora_inizio, durata, artista, descrizione, genere, pubblicato, id_creatore, id_palco) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        conn.execute(insert_query, (day, start_hour, duration, artist, description, genre, published, stage_id))
        return True, None
    
    except Exception as e:
        conn.rollback()
        return False, "DATABASE_ERROR"

def get_overlapping_published_shows(day, hour_slot, duration, conn):
    # Returns all published shows that overlap with the given interval (start hour, duration),
    # also considering the possibility that the show extends past midnight (next day).

    cursor = conn.cursor()
    
    start = int(hour_slot)
    end = start + int(duration)
    
    query = """
        SELECT * FROM SPETTACOLI 
        WHERE pubblicato = 'True' AND (
            (giorno = ? AND (
                (? < slot_orario + durata) AND (slot_orario < ?)
            ))
            OR
            (giorno = ? + 1 AND (
                slot_orario < (? - 24)
            ))
        );
    """
    
    cursor.execute(query, (day, start, end, day, end))
    shows = cursor.fetchall()
    return shows

def is_already_performing(artist):
    try:
        conn = sqlite3.connect('/musical-festival-website/musical_festival.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT artista FROM SPETTACOLI WHERE artista = ?;"
        cursor.execute(query, (artist, ))

        shows = cursor.fetchone()
        conn.close()
        if shows:
            return True
        return False
    except Exception as e:
        return False, "DATABASE_ERROR_IS_ALREADY_PERFORMING"

