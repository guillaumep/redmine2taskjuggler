import codecs
import argparse
import datetime

from redmine2taskjuggler import taskjuggler
from redmine2taskjuggler.config_reader import get_config
from redmine2taskjuggler.sqlite_factory import get_sqlite_connection

SELECT_ISSUE_IDS = """\
  SELECT id FROM issue
"""

SELECT_ISSUES = """\
  SELECT issue.*, user.email as assignee_email, milestone.name as milestone_name
  FROM issue
  LEFT JOIN user ON issue.assigned_to = user.id
  LEFT JOIN milestone ON issue.milestone_id = milestone.id
"""

NOT_ASSIGNED = 'not_assigned'
BACKLOG_MILESTONE_ID = 'backlog_milestone'

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

def get_issue_ids(conn):
    curs = conn.cursor()
    curs.execute(SELECT_ISSUE_IDS)
    ids = set((row['id'] for row in curs))
    conn.commit()
    return ids

def main():
    args = parse_args()
    conf = get_config()
    conn = get_sqlite_connection()

    tasks = {}
    issue_parent = {}

    ignored_milestones = conf['taskjuggler'].get('ignore_milestones', '')
    ignored_milestones = set((int(i.strip()) for i in ignored_milestones.split(',')))

    task_id_prefix = conf['taskjuggler']['task_id_prefix']
    milestone_id_prefix = conf['taskjuggler']['milestone_id_prefix']

    issue_ids = get_issue_ids(conn)

    backlog_milestone_task = taskjuggler.Task(
         id=BACKLOG_MILESTONE_ID,
         name='Backlog',
         effort=0.0,
         assignee=NOT_ASSIGNED,
         priority=100 # low priority
     )

    if conf['taskjuggler'].get('project_start'):
        project_start_date = datetime.datetime.strptime(conf['taskjuggler']['project_start'], '%Y-%m-%d')
    else:
        project_start_date = datetime.datetime.now()


    for issue in get_issues(conn):
        if issue['milestone_id'] in ignored_milestones:
            continue

        effort = issue['estimated_hours'] or conf['taskjuggler'].get('default_effort', 8.0)
        effort = float(effort)

        # Remaining effort can only be specified inside a timesheet
        # and not inside a task
        #remaining = None
        #if issue['done_ratio']:
        #    remaining = effort - (effort * int(issue['done_ratio']) / 100.0)

        # Consider due date if it is in the project scope
        # This is being commented out because the data contains conflicts
        # and cannot be scheduled
        #due_date = None
        #if issue['due_date']:
        #    due_date = datetime.datetime.strptime(issue['due_date'], '%Y-%m-%d')
        #    if due_date < project_start_date:
        #        due_date = None

        task = taskjuggler.Task(
            id=task_id_prefix + str(issue['id']),
            name="#%s: %s" % (str(issue['id']), issue['subject']),
            effort=effort,
            assignee=taskjuggler.email_to_taskjuggler_id(issue['assignee_email']) or NOT_ASSIGNED
            #end_date=due_date
        )
        tasks[issue['id']] = task
        # The parent id must refer to an issue we have imported from Redmine.
        # Otherwise, it means the parent issue was closed
        # (we only import open issues from Redmine)
        if issue['parent_id'] and issue['parent_id'] in issue_ids:
            issue_parent[issue['id']] = issue['parent_id']
        elif issue['milestone_id']:
            # If the issue has no parent, we create one based on
            # the milestone/sprint
            milestone_id = milestone_id_prefix + str(issue['milestone_id'])
            milestone_task = tasks.setdefault(milestone_id,
                taskjuggler.Task(
                    id=milestone_id,
                    name=issue['milestone_name'],
                    effort=0.0,
                    assignee=NOT_ASSIGNED
                )
            )
            issue_parent[issue['id']] = milestone_id
        else:
            # Issues with no parent and no milestone will be assigned to a
            # special 'backlog' milestone
            backlog_milestone_task = tasks.setdefault(BACKLOG_MILESTONE_ID, backlog_milestone_task)
            issue_parent[issue['id']] = BACKLOG_MILESTONE_ID

    for child_id, parent_id in issue_parent.iteritems():
        child_task = tasks.get(child_id)
        parent_task = tasks.get(parent_id)
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
