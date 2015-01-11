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

def convert_id(s):
    def _convert_id(s):
        for c in s:
            if c in string.ascii_letters or c in string.digits:
                yield c
            else:
                yield '_'
    return ''.join(_convert_id(s))

def main():
    redmine = get_redmine()
    conf = get_config()
    conn = get_sqlite_connection()
    conn.execute("DELETE FROM users")
    for user in get_redmine_users(redmine):
        taskjuggler_id = user.mail
        domain_to_remove = conf['taskjuggler'].get('remove_domain_from_id')
        if domain_to_remove and taskjuggler_id.endswith(domain_to_remove):
            taskjuggler_id = taskjuggler_id.replace(domain_to_remove, '')
        taskjuggler_id = convert_id(taskjuggler_id)
        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
            (user.id, taskjuggler_id, user.firstname, user.lastname, user.mail))
    conn.commit()

if __name__ == '__main__':
    main()
