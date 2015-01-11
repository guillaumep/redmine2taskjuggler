import codecs
import argparse

from redmine2taskjuggler import taskjuggler
from redmine2taskjuggler.sqlite_factory import get_sqlite_connection

SELECT_ISSUES = """\
  SELECT issue.*, user.email as assignee_email FROM issue
  LEFT JOIN user ON issue.assigned_to = user.id
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

    tasks = {}
    issue_parent = {}
    for issue in get_issues(conn):
        task = taskjuggler.Task(
            id=issue['id'],
            name="#%s: %s" % (str(issue['id']), issue['subject']),
            effort=issue['estimated_hours'] or 8.0,
            assignee=taskjuggler.email_to_taskjuggler_id(issue['assignee_email']) or 'not_assigned'
        )
        tasks[task.id] = task
        if issue['parent_id']:
            issue_parent[issue['id']] = issue['parent_id']

    for child_id, parent_id in issue_parent.iteritems():
        child_task = tasks.get(child_id)
        parent_task = tasks.get(parent_id)
        # It is possible the parent task is a closed task,
        # and currently closed tasks are not imported
        if parent_task:
            child_task.parent = parent_task
            parent_task.children.append(child_task)

    with codecs.open(args.output, 'w', encoding='utf8') as tjout:
        tjout.write("task outbox 'All Outbox tickets' {\n")
        for task_id in sorted(tasks.iterkeys()):
            task = tasks[task_id]
            # Child tasks will be written recursively by their parent
            if task.parent: continue
            tjout.write(task.to_taskjuggler_language())
            tjout.write('\n')
        tjout.write('}\n')

if __name__ == '__main__':
    main()
