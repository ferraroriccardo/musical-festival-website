import sqlite3
from . import palchi_dao
from .settings_dao import DB_PATH, time_to_minutes

def get_shows():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM SPETTACOLI ORDER BY SPETTACOLI.giorno, SPETTACOLI.ora_inizio;"
        cursor.execute(query)

        shows = cursor.fetchall()
        return shows
    except Exception as e:
        return False, "DATABASE_ERROR_GET_SHOWS"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
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

    if stage != -1 and stage != "-1" and stage != "all":
        try:
            stage_id = int(stage)
            query += " AND id_palco = ?"
            params.append(stage_id)
        except Exception:
            from .palchi_dao import get_palco_by_name
            palco_id = get_palco_by_name(stage)
            if palco_id is not None:
                query += " AND id_palco = ?"
                params.append(palco_id)
    if genre != "all":
        query += " AND genere = ?"
        params.append(genre)
    if published:
        query += " AND pubblicato = ?"
        params.append(published)
    
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
        query += " ORDER BY SPETTACOLI.giorno, SPETTACOLI.ora_inizio"

        cursor.execute(query, params)
        shows = cursor.fetchall()
        return shows
    except Exception as e:
        return False, "DATABASE_ERROR_GET_SHOWS_FILTERED"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def create_event(day, start_hour, duration, artist, description, playlist_link, img_path, genre, published, creator_id, stage_name, draft_id=None):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        stage_id = palchi_dao.get_palco_by_name(stage_name)
        if stage_id is None:
            return False, "STAGE_NOT_FOUND"

        if exist_overlapping_published_shows(day, start_hour, duration, stage_id, conn):
            return False, "SHOW_SLOT_ALREADY_OCCUPIED"
        if published == 1 and is_already_performing(artist, conn):
            return False, "ARTIST_ALREADY_PERFORMING"

        if draft_id is not None:
            update_query = """
                UPDATE SPETTACOLI
                SET giorno = ?, ora_inizio = ?, durata = ?, artista = ?, descrizione = ?, link_playlist = ?,
                    path_immagine = ?, genere = ?, pubblicato = ?, id_creatore = ?, id_palco = ?
                WHERE id = ?;
            """
            cursor.execute(update_query, (day, start_hour, duration, artist, description, playlist_link, img_path,
                genre, published, creator_id, stage_id, draft_id))
            conn.commit()
            return True, None
        else:
            insert_query = """
                INSERT INTO SPETTACOLI (giorno, ora_inizio, durata, artista, descrizione, link_playlist, path_immagine, genere, pubblicato, id_creatore, id_palco)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(insert_query, (day, start_hour, duration, artist, description, playlist_link, img_path, genre, published, creator_id, stage_id))
            conn.commit()
            return True, None
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return False, "DATABASE_ERROR_CREATE_EVENT"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def update_draft(draft_id, day, start_hour, duration, artist, description, playlist_link, img_path,
            genre, published, creator_id, stage_name):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        stage_id = palchi_dao.get_palco_by_name(stage_name)
        if stage_id is None:
            return False, "STAGE_NOT_FOUND"

        if exist_overlapping_published_shows(day, start_hour, duration, stage_id, conn, exclude_id=draft_id):
            return False, "SHOW_SLOT_ALREADY_OCCUPIED"
        if published == 1:
            if is_already_performing(artist, conn):
                return False, "ARTIST_ALREADY_PERFORMING"

        update_query = """
            UPDATE SPETTACOLI
            SET giorno = ?, ora_inizio = ?, durata = ?, artista = ?, descrizione = ?, link_playlist = ?,
                path_immagine = ?, genere = ?, pubblicato = ?, id_creatore = ?, id_palco = ?
            WHERE id = ?;
        """

        cursor.execute(update_query, (day, start_hour, duration, artist, description, playlist_link, img_path,
            genre, published, creator_id, stage_id, draft_id))
        conn.commit()

        return True, None

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return False, "DATABASE_ERROR_CREATE_EVENT"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def exist_overlapping_published_shows(day, hour_slot, duration, stage, conn, exclude_id=None):
    try:
        cursor = conn.cursor()

        new_start = time_to_minutes(hour_slot)
        new_end = new_start + int(duration)

        query = """
            SELECT id, ora_inizio, durata
            FROM SPETTACOLI
            WHERE pubblicato = 1
              AND giorno = ?
              AND id_palco = ?
        """

        cursor.execute(query, (day, stage))
        shows = cursor.fetchall()
        for row in shows:
            existing_start = time_to_minutes(row["ora_inizio"])
            existing_duration = int(row["durata"])
            existing_end = existing_start + existing_duration

            if new_start < existing_end and existing_start < new_end:
                return True

        return False

    except Exception as e:
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()


def is_already_performing(artist, conn):
    cursor = conn.cursor()
    try:
        query = "SELECT artista FROM SPETTACOLI WHERE artista = ? AND pubblicato = 1;"
        cursor.execute(query, (artist,))
        return cursor.fetchone() is not None
    except Exception as e:
        return False
    finally:
        if 'cursor' in locals():
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
            WHERE SPETTACOLI.id_creatore = ? AND SPETTACOLI.pubblicato = ?
            ORDER BY SPETTACOLI.giorno, SPETTACOLI.ora_inizio;
        """
        cursor.execute(query, (user_id, 0))

        shows = cursor.fetchall()
        return shows
    
    except Exception as e:
        return False, "DATABASE_ERROR_GET_DRAFTS"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def get_published(creator_id):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT SPETTACOLI.*, PALCHI.nome AS nome_palco, UTENTI.email AS email_creatore
            FROM SPETTACOLI
            JOIN PALCHI ON SPETTACOLI.id_palco = PALCHI.id
            JOIN UTENTI ON SPETTACOLI.id_creatore = UTENTI.id
            WHERE SPETTACOLI.pubblicato = ?
            AND SPETTACOLI.id_creatore = ?
            ORDER BY SPETTACOLI.giorno, SPETTACOLI.ora_inizio;
        """        
        cursor.execute(query, (1, creator_id))

        shows = cursor.fetchall()
        return shows
    except Exception as e:
        return False, "DATABASE_ERROR_GET_PUBLISHED"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
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
            WHERE SPETTACOLI.pubblicato = ?
            AND SPETTACOLI.artista = ?;
        """      
        cursor.execute(query, (1, artist_name))

        artist = cursor.fetchone()
        return artist
    except Exception as e:
        return False, "DATABASE_ERROR_GET_ARTIST_BY_NAME"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def get_genres():
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT DISTINCT(genere) FROM SPETTACOLI;"      
        cursor.execute(query)

        genres_raw = cursor.fetchall()
        genres = [g[0] for g in genres_raw if g[0] is not None]

        return genres
    except Exception as e:
        return False, "DATABASE_ERROR_GET_ARTIST_BY_NAME"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def draft_exist(draft_id):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT id FROM SPETTACOLI WHERE id = ? AND pubblicato = 0;"
        cursor.execute(query, (draft_id,))

        draft = cursor.fetchone()
        return draft is not None
    except Exception as e:
        return False, "DATABASE_ERROR_DRAFT_EXIST"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
