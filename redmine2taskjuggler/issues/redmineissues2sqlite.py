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

def main():
    redmine = get_redmine()
    conf = get_config()
    conn = get_sqlite_connection()
    conn.execute("DELETE FROM issue")
    conn.execute("DELETE FROM milestone")
    milestones = {}
    for issue in get_redmine_issues(redmine):
        milestone = get_optional_field(issue, 'fixed_version')
        if milestone:
            if milestone.id not in milestones:
                milestones[milestone.id] = milestone.name
        conn.execute("INSERT INTO issue VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (issue.id,
             get_optional_field_id(issue, 'parent'),
             milestone.id if milestone else None,
             issue.subject,
             get_optional_field_id(issue, 'assigned_to'),
             get_optional_field(issue, 'estimated_hours'),
             issue.done_ratio,
             get_optional_field(issue, 'due_date'),
             issue.updated_on))

    for id, name in milestones.iteritems():
        conn.execute("INSERT INTO milestone VALUES (?, ?)",
            (id, name))

    conn.commit()

if __name__ == '__main__':
    main()
