import codecs
import argparse

from redmine2taskjuggler import taskjuggler
from redmine2taskjuggler.sqlite_factory import get_sqlite_connection

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('output',
        help='File name of the output (TaskJuggler format). Example: resources.tji')
    return parser.parse_args()

def get_users(conn):
    curs = conn.cursor()
    curs.execute("SELECT * FROM user")
    for row in curs:
        yield row
    conn.commit()

def main():
    args = parse_args()
    conn = get_sqlite_connection()
    with codecs.open(args.output, 'w', encoding='utf8') as tjout:
        for user in get_users(conn):
            resource_name = user['first_name'] + ' ' + user['last_name']
            resource_name = resource_name.strip()
            resource = taskjuggler.Resource(
                id=user['id'],
                name=resource_name,
                email=user['email'])
            tjout.write(resource.to_taskjuggler_language())
            tjout.write('\n')

        # Special resource: not assigned
        resource = taskjuggler.Resource(
            id=0,
            name='Not assigned',
            email='not_assigned'
        )
        tjout.write(resource.to_taskjuggler_language())
        tjout.write('\n')

if __name__ == '__main__':
    main()
