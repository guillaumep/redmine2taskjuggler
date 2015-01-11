"""
This script will delete the users table
and replace it with content from redmine
"""
import string

from redmine2taskjuggler.config_reader import get_config
from redmine2taskjuggler.redmine_factory import get_redmine
from redmine2taskjuggler.sqlite_factory import get_sqlite_connection

def get_redmine_users(redmine, limit=None):
    params = {}
    if limit:
        params['limit'] = limit
    for user in redmine.user.all(**params):
        yield user

def main():
    redmine = get_redmine()
    conf = get_config()
    conn = get_sqlite_connection()
    conn.execute("DELETE FROM user")
    for user in get_redmine_users(redmine):
        conn.execute("INSERT INTO user VALUES (?, ?, ?, ?)",
            (user.id, user.firstname, user.lastname, user.mail))
    conn.commit()

if __name__ == '__main__':
    main()
