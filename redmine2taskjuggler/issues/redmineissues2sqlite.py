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

def main():
    redmine = get_redmine()
    conf = get_config()
    conn = get_sqlite_connection()
    conn.execute("DELETE FROM issues")
    for issue in get_redmine_issues(redmine):
        taskjuggler_id = conf['taskjuggler']['task_id_suffix'] + str(issue.id)
        assigned_to = None
        issue_assigned_to = get_optional_field(issue, 'assigned_to')
        if issue_assigned_to is not None:
            assigned_to = issue_assigned_to.id
        conn.execute("INSERT INTO issues VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (issue.id,
             taskjuggler_id,
             issue.subject,
             assigned_to,
             get_optional_field(issue, 'estimated_hours'),
             issue.done_ratio, 
             get_optional_field(issue, 'due_date'),
             issue.updated_on))
    conn.commit()

if __name__ == '__main__':
    main()
