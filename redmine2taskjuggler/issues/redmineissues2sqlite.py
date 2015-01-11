"""
This script will delete the issues table
and replace it with content from redmine
"""
import string

from redmine2taskjuggler.config_reader import get_config
from redmine2taskjuggler.redmine_factory import get_redmine
from redmine2taskjuggler.sqlite_factory import get_sqlite_connection

def get_redmine_issues(redmine, limit=None):
    params = {}
    if limit:
        params['limit'] = limit
    for issue in redmine.issue.all(**params):
        yield issue

def get_optional_field(issue, field):
    if hasattr(issue, field):
        return getattr(issue, field)
    else:
        return None

def get_optional_field_id(issue, field):
    field_value = get_optional_field(issue, field)
    if field_value is not None:
        return field_value.id
    else:
        return None

def insert_issue(issue, conn, conf):
    conn.execute("INSERT INTO issue VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (issue.id,
         get_optional_field_id(issue, 'parent'),
         issue.subject,
         get_optional_field_id(issue, 'assigned_to'),
         get_optional_field(issue, 'estimated_hours'),
         issue.done_ratio,
         get_optional_field(issue, 'due_date'),
         issue.updated_on))


def main():
    redmine = get_redmine()
    conf = get_config()
    conn = get_sqlite_connection()
    conn.execute("DELETE FROM issue")
    for issue in get_redmine_issues(redmine):
        insert_issue(issue, conn, conf)
    conn.commit()

if __name__ == '__main__':
    main()
