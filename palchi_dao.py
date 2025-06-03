import sqlite3

def get_palco_by_name(stage_name):
    conn = sqlite3.connect('musical-festival-website/musical_festival.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT id FROM PALCHI WHERE nome = ?;"

    cursor.execute(query, (stage_name, ))
    id = cursor.fetchone

    conn.close()
    return id