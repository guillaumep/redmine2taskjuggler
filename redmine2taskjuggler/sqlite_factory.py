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

CREATE_ISSUES_TABLE = """\
CREATE TABLE IF NOT EXISTS issues (
    redmine_id INTEGER PRIMARY KEY ASC,
    taskjuggler_id TEXT,
    subject TEXT,
    assigned_to INTEGER,
    estimated_hours REAL,
    done_ratio INTEGER,
    due_date INTEGER,
    updated_on INTEGER
)
"""

def get_sqlite_connection():
    config = get_config()
    conn = sqlite3.connect(config['sqlite']['dbname'])

    global DB_INITIALIZED
    if not DB_INITIALIZED:
        conn.execute(CREATE_USERS_TABLE)
        conn.execute(CREATE_ISSUES_TABLE)
        DB_INITIALIZED = True

    # https://docs.python.org/2/library/sqlite3.html#sqlite3.Row
    conn.row_factory = sqlite3.Row
    return conn
