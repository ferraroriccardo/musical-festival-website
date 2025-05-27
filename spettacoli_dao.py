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
