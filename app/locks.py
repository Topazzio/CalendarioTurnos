import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("locks.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS locks (
    start_time TEXT PRIMARY KEY,
    expires_at TEXT
)
""")

conn.commit()

def create_lock(start_time):
    expires = datetime.utcnow() + timedelta(minutes=5)

    cursor.execute(
        "INSERT OR REPLACE INTO locks VALUES (?, ?)",
        (start_time, expires.isoformat())
    )
    conn.commit()


def is_locked(start_time):

    cursor.execute(
        "SELECT expires_at FROM locks WHERE start_time=?",
        (start_time,)
    )

    row = cursor.fetchone()

    if not row:
        return False

    expires = datetime.fromisoformat(row[0])

    if datetime.utcnow() > expires:
        cursor.execute("DELETE FROM locks WHERE start_time=?", (start_time,))
        conn.commit()
        return False

    return True
#a a a
# Hola soy un comentario para probar el commit. Se me cuidan
# Esto esta hecho con vibe coding. Es mas inseguro que caminar por la villa 31. si usas esto en algun proyecto be advised, esta hecho con las patas.
def remove_lock(start_time):
    cursor.execute("DELETE FROM locks WHERE start_time=?", (start_time,))
    conn.commit()

