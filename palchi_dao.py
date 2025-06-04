import sqlite3

def get_palco_by_name(stage_name):
    try:
        conn = sqlite3.connect('musical_festival.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT id FROM PALCHI WHERE nome = ?;"

        cursor.execute(query, (stage_name, ))
        id = cursor.fetchone

        conn.close()
        return id
    except Exception as e:
        return False, "DATABASE_ERROR_GET_PALCO_BY_NAME"