import sqlite3
from . import palchi_dao
from .settings_dao import DB_PATH, time_to_minutes

def get_shows():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
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

def set_params(query, day, stage, genre, published):
    params = []
    match day:
            case 1:
                query += " AND giorno = ?"
                params.append("friday 20th")
            case 2:
                query += " AND giorno = ?"
                params.append("saturday 21st")
            case 3:
                query += " AND giorno = ?"
                params.append("sunday 22nd")
    if stage in [0,1,2]:
            query += " AND id_palco = ?"
            params.append(stage)
    if genre != "all":
        query += " AND genere = ?"
        params.append(genre)
    if published:
        query += " AND pubblicato = ?"
        params.append(published)
        
    query += ";"
    return query, params

def get_shows_filtered(day, stage, genre, published):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT SPETTACOLI.*, PALCHI.nome AS nome_palco, UTENTI.email AS email_creatore
            FROM SPETTACOLI
            JOIN PALCHI ON SPETTACOLI.id_palco = PALCHI.id
            JOIN UTENTI ON SPETTACOLI.id_creatore = UTENTI.id
        """
        query, params = set_params(query, day, stage, genre, published)

        cursor.execute(query, params)
        shows = cursor.fetchall()
        return shows
    except Exception as e:
        return False, "DATABASE_ERROR_GET_SHOWS_FILTERED"
    finally:
        cursor.close()
        conn.close()

def create_event(day, start_hour, duration, artist, description, img_path, genre, published, creator_id, stage_name):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        stage_id = palchi_dao.get_palco_by_name(stage_name)
        if stage_id is None:
            return False, "STAGE_NOT_FOUND"

        if published == 1 :
            if exist_overlapping_published_shows(day, start_hour, duration, stage_id, conn):
                return False, "SHOW_SLOT_ALREADY_OCCUPIED"
            
            if is_already_performing(artist, conn):
                return False, "ARTIST_ALREADY_PERFORMING"

        insert_query = """
            INSERT INTO SPETTACOLI (giorno, ora_inizio, durata, artista, descrizione, path_immagine, genere, pubblicato, id_creatore, id_palco)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        
        print(f"Valori passati a execute: {(day, start_hour, duration, artist, description, img_path, genre, published, creator_id, stage_id)}")
        print(f"Numero valori: {len((day, start_hour, duration, artist, description, img_path, genre, published, creator_id, stage_id))}")

        cursor.execute(insert_query, (day, start_hour, duration, artist, description, img_path, genre, published, creator_id, stage_id))
        conn.commit()

        return True, None

    except Exception as e:
        print("Errore durante la creazione evento:", e)
        if 'conn' in locals():
            conn.rollback()
        return False, "DATABASE_ERROR_CREATE_EVENT"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def update_draft(draft_id, day, start_hour, duration, artist, description, img_path,
            genre, published, creator_id, stage_name):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if published == 1 :
            if exist_overlapping_published_shows(day, start_hour, duration, stage_id, conn):
                return False, "SHOW_SLOT_ALREADY_OCCUPIED"
            
            if is_already_performing(artist, conn):
                return False, "ARTIST_ALREADY_PERFORMING"

        stage_id = palchi_dao.get_palco_by_name(stage_name)
        if stage_id is None:
            return False, "STAGE_NOT_FOUND"

        update_query = """
            UPDATE SPETTACOLI
            SET giorno = ?, ora_inizio = ?, durata = ?, artista = ?, descrizione = ?,
                path_immagine = ?, genere = ?, pubblicato = ?, id_creatore = ?, id_palco = ?
            WHERE id = ?;
        """

        cursor.execute(update_query, (day, start_hour, duration, artist, description, img_path,
            genre, published, creator_id, stage_id, draft_id))
        conn.commit()

        return True, None

    except Exception as e:
        print("Errore durante la creazione evento:", e)
        if 'conn' in locals():
            conn.rollback()
        return False, "DATABASE_ERROR_CREATE_EVENT"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def exist_overlapping_published_shows(day, hour_slot, duration, stage, conn):
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM SPETTACOLI WHERE pubblicato = '1' AND giorno = ? AND id_palco = ?;"
        
        start = time_to_minutes(hour_slot)
        end = start + int(duration)

        cursor.execute(query, (day, stage))
        shows = []

        for row in cursor.fetchall():
            other_start = time_to_minutes(row['ora_inizio'])
            other_end = other_start + row['durata']
            if start < other_end and other_start < end:
                shows.append(row)

        return len(shows) > 0
    except Exception as e:
        print("Errore overlapping:", e)
        return False
    finally:
        cursor.close()

def is_already_performing(artist, conn):
    cursor = conn.cursor()
    try:
        query = "SELECT artista FROM SPETTACOLI WHERE artista = ? AND pubblicato = 1;"
        cursor.execute(query, (artist,))
        return cursor.fetchone() is not None
    except Exception as e:
        print("Errore checking performer:", e)
        return False
    finally:
        cursor.close()


def get_drafts(user_id):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT SPETTACOLI.*, PALCHI.nome AS nome_palco, UTENTI.email AS email_creatore
            FROM SPETTACOLI
            JOIN PALCHI ON SPETTACOLI.id_palco = PALCHI.id
            JOIN UTENTI ON SPETTACOLI.id_creatore = UTENTI.id
            WHERE SPETTACOLI.id_creatore = ? AND SPETTACOLI.pubblicato = ?;
        """
        cursor.execute(query, (user_id, 0))

        shows = cursor.fetchall()
        return shows
    
    except Exception as e:
        conn.rollback()
        return False, "DATABASE_ERROR_GET_DRAFTS"
    finally:
        cursor.close()
        conn.close()

def get_published():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT SPETTACOLI.*, PALCHI.nome AS nome_palco, UTENTI.email AS email_creatore
            FROM SPETTACOLI
            JOIN PALCHI ON SPETTACOLI.id_palco = PALCHI.id
            JOIN UTENTI ON SPETTACOLI.id_creatore = UTENTI.id
            WHERE SPETTACOLI.pubblicato = ?;
        """        
        cursor.execute(query, (1, ))

        shows = cursor.fetchall()
        return shows
    except Exception as e:
        return False, "DATABASE_ERROR_GET_PUBLISHED"
    finally:
        cursor.close()
        conn.close()

def get_artist_by_name(artist_name):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT SPETTACOLI.*, PALCHI.nome AS nome_palco, UTENTI.email AS email_creatore
            FROM SPETTACOLI
            JOIN PALCHI ON SPETTACOLI.id_palco = PALCHI.id
            JOIN UTENTI ON SPETTACOLI.id_creatore = UTENTI.id
            AND SPETTACOLI.artista = ?
            WHERE SPETTACOLI.pubblicato = ?;
        """      
        cursor.execute(query, (artist_name, 1))

        artist = cursor.fetchone()
        return artist
    except Exception as e:
        return False, "DATABASE_ERROR_GET_ARTIST_BY_NAME"
    finally:
        cursor.close()
        conn.close()

def get_genres():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT DISTINCT(genere) FROM SPETTACOLI;"      
        cursor.execute(query)

        genres = cursor.fetchall()
        return genres
    except Exception as e:
        return False, "DATABASE_ERROR_GET_ARTIST_BY_NAME"
    finally:
        cursor.close()
        conn.close()