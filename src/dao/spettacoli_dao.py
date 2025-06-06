import sqlite3
from . import palchi_dao
from .settings_dao import DB_PATH, time_to_minutes

def get_shows():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM SPETTACOLI;"
        cursor.execute(query)

        shows = cursor.fetchall()
        return shows
    except Exception as e:
        return False, "DATABASE_ERROR_GET_SHOWS"
    finally:
        cursor.close()
        conn.close()

def get_shows_filtered(giorno, palco, genere):
    try:
        conn = sqlite3.connect(DB_PATH)
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
    finally:
        cursor.close()
        conn.close()

def create_event(day, start_hour, duration, artist, description, genre, published, creator_id, stage_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        overlapping = exist_overlapping_published_shows(day, start_hour, duration, conn)
        if published == 1 and overlapping:
            return False, "SHOW_SLOT_ALREADY_OCCUPIED"

        artist_already_performing = is_already_performing(artist, conn)
        if published and artist_already_performing:
            return False, "ARTIST_ALREADY_PERFORMING"

        stage_id = palchi_dao.get_palco_by_name(stage_name)
        if stage_id is None:
            return False, "STAGE_NOT_FOUND"

        insert_query = """
            INSERT INTO SPETTACOLI (giorno, ora_inizio, durata, artista, descrizione, genere, pubblicato, id_creatore, id_palco)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        print(f"Valori passati a execute: {(day, start_hour, duration, artist, description, genre, published, creator_id, stage_id)}")
        print(f"Numero valori: {len((day, start_hour, duration, artist, description, genre, published, creator_id, stage_id))}")

        cursor.execute(insert_query, (day, start_hour, duration, artist, description, genre, published, creator_id, stage_id))
        conn.commit()

        return True, None

    except Exception as e:
        print("Errore durante la creazione evento:", e)  # stampa l'errore sulla console
        if 'conn' in locals():
            conn.rollback()
        return False, "DATABASE_ERROR_CREATE_EVENT"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def exist_overlapping_published_shows(day, hour_slot, duration, conn):
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM SPETTACOLI WHERE pubblicato = '1' AND giorno = ?;"
        
        start = time_to_minutes(hour_slot)
        end = start + int(duration)

        # Seleziona tutti gli show pubblicati in quel giorno
        cursor.execute(query, (day, ))
        shows = []

        for row in cursor.fetchall():
            other_start = time_to_minutes(row['ora_inizio'])
            other_end = other_start + row['durata']
            
            # Verifica sovrapposizione (anche parziale)
            if start < other_end and other_start < end:
                shows.append(row)

        return len(shows) > 0

    except Exception as e:
        print("Errore overlapping:", e)
        return False, "DATABASE_ERROR_GET_OVERLAPPING_PUBLISHED_SHOWS"

def is_already_performing(artist, conn):
    try:
        cursor = conn.cursor()

        query = "SELECT artista FROM SPETTACOLI WHERE artista = ?;"
        cursor.execute(query, (artist, ))

        shows = cursor.fetchone()
        if shows:
            return True
        return False
    except Exception as e:
        conn.rollback()
        return False, "DATABASE_ERROR_IS_ALREADY_PERFORMING"

def get_drafts(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM SPETTACOLI WHERE id_creatore = ? AND pubblicato = ?;"
        cursor.execute(query, (user_id, 0))

        shows = cursor.fetchall()
        return shows
    
    except Exception as e:
        conn.rollback()
        return False, "DATABASE_ERROR_GET_DRAFTS"
    finally:
        cursor.close()
        conn.close()