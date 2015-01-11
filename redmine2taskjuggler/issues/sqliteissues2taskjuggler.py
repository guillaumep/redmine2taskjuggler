import codecs
import argparse

from redmine2taskjuggler import taskjuggler
from redmine2taskjuggler.sqlite_factory import get_sqlite_connection

SELECT_ISSUES = """\
  SELECT issues.*, users.taskjuggler_id as assignee FROM issues
  LEFT JOIN users ON issues.assigned_to = users.redmine_id
"""

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('output',
        help='File name of the output (TaskJuggler format). Example: redmine_tasks.tji')
    return parser.parse_args()

def get_issues(conn):
    curs = conn.cursor()
    curs.execute(SELECT_ISSUES)
    for row in curs:
        yield row
    conn.commit()

def main():
    args = parse_args()
    conn = get_sqlite_connection()
    with codecs.open(args.output, 'w', encoding='utf8') as tjout:
        tjout.write("task outbox 'All Outbox tickets' {\n")
        for issue in get_issues(conn):
            if not issue['assignee']: continue
            task = taskjuggler.Task(
                id=issue['taskjuggler_id'],
                name="#%s: %s" % (str(issue['redmine_id']), issue['subject']),
                effort=1,
                assignee=issue['assignee']
            )
            tjout.write(task.to_taskjuggler_language())
            tjout.write('\n')
        tjout.write('}\n')

if __name__ == '__main__':
    main()
