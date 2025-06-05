import sqlite3
from settings_dao import DB_PATH

def get_palco_by_name(stage_name):
    conn = sqlite3.connect('musical-festival-website/musical_festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT id FROM PALCHI WHERE nome = ?;"

        cursor.execute(query, (stage_name, ))
        id = cursor.fetchone

        conn.close()
        return id
    except Exception as e:
        return False, "DATABASE_ERROR_GET_PALCO_BY_NAME"
    finally:
        cursor.close()
        conn.close()