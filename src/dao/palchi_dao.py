import sqlite3
from .settings_dao import DB_PATH

def get_palco_by_name(stage_name):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT id FROM PALCHI WHERE nome = ?;"

        cursor.execute(query, (stage_name, ))
        row = cursor.fetchone()

        if row:
            return row['id']
        return None
    
    except Exception as e:
        return False, "DATABASE_ERROR_GET_PALCO_BY_NAME"
    finally:
        cursor.close()
        conn.close()

def get_stages():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT nome FROM PALCHI;"

        cursor.execute(query)
        stages = cursor.fetchall()

        return stages
    except Exception as e:
        return False, "DATABASE_ERROR_GET_STAGES"
    finally:
        cursor.close()
        conn.close()