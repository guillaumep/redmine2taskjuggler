import sqlite3

from config_reader import get_config

DB_INITIALIZED = False

CREATE_USERS_TABLE = """\
CREATE TABLE IF NOT EXISTS users (
    redmine_id INTEGER PRIMARY KEY ASC,
    taskjuggler_id TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT
)
"""

def get_sqlite_connection():
    config = get_config()
    conn = sqlite3.connect(config['sqlite']['dbname'])

    global DB_INITIALIZED
    if not DB_INITIALIZED:
        conn.execute(CREATE_USERS_TABLE)
        DB_INITIALIZED = True

    # https://docs.python.org/2/library/sqlite3.html#sqlite3.Row
    conn.row_factory = sqlite3.Row
    return conn
