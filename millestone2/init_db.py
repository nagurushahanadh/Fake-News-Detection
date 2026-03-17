import sqlite3

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS processed_text (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original TEXT,
            processed TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_id INTEGER,
            entity TEXT,
            label TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_processed_text(original, processed):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("INSERT INTO processed_text (original, processed) VALUES (?, ?)",
              (original, processed))

    text_id = c.lastrowid
    conn.commit()
    conn.close()

    return text_id


def insert_entity(text_id, entity, label):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("INSERT INTO entities (text_id, entity, label) VALUES (?, ?, ?)",
              (text_id, entity, label))

    conn.commit()
    conn.close()