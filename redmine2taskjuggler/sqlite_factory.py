import sqlite3

from config_reader import get_config

DB_INITIALIZED = False

CREATE_USER_TABLE = """\
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY ASC,
    first_name TEXT,
    last_name TEXT,
    email TEXT
)
"""

CREATE_ISSUE_TABLE = """\
CREATE TABLE IF NOT EXISTS issue (
    id INTEGER PRIMARY KEY ASC,
    parent_id INTEGER,
    milestone_id INTEGER,
    subject TEXT,
    assigned_to INTEGER,
    estimated_hours REAL,
    done_ratio INTEGER,
    due_date INTEGER,
    updated_on INTEGER
)
"""

CREATE_MILESTONE_TABLE = """\
CREATE TABLE IF NOT EXISTS milestone (
    id INTEGER PRIMARY KEY ASC,
    name TEXT
)
"""

def get_sqlite_connection():
    config = get_config()
    conn = sqlite3.connect(config['sqlite']['dbname'])

    global DB_INITIALIZED
    if not DB_INITIALIZED:
        conn.execute(CREATE_USER_TABLE)
        conn.execute(CREATE_ISSUE_TABLE)
        conn.execute(CREATE_MILESTONE_TABLE)
        DB_INITIALIZED = True

    # https://docs.python.org/2/library/sqlite3.html#sqlite3.Row
    conn.row_factory = sqlite3.Row
    return conn
