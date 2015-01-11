import string
from redmine2taskjuggler.config_reader import get_config

def email_to_taskjuggler_id(email):
    if email is None:
        return None

    def _convert_id(s):
        for c in s:
            if c in string.ascii_letters or c in string.digits:
                yield c
            else:
                yield '_'

    taskjuggler_id = email
    domain_to_remove = get_config()['taskjuggler'].get('remove_domain_from_id')
    if domain_to_remove and taskjuggler_id.endswith(domain_to_remove):
        taskjuggler_id = taskjuggler_id.replace(domain_to_remove, '')

    return ''.join(_convert_id(taskjuggler_id))


class Resource:
    def __init__(self, id, name, email=None):
        self.id = id
        self.name = name
        self.email = email

    @property
    def taskjuggler_id(self):
        return email_to_taskjuggler_id(self.email)

    def to_taskjuggler_language(self):
        output = u"""\
resource %(id)s '%(name)s'
{ email '%(email)s' }
"""     % dict(id=self.taskjuggler_id,
               name=quoted_string(self.name),
               email=self.email)
        return output

class Task:
    def __init__(self, id, name, effort, assignee=None):
        self.id = id
        self.name = name
        self.effort = effort # in hours
        self.assignee = assignee
        self.parent = None
        self.children = []

    @property
    def taskjuggler_id(self):
        return get_config()['taskjuggler']['task_id_prefix'] + str(self.id)

    def to_taskjuggler_language(self):
        attributes = ""
        if self.children:
            for child in self.children:
                attributes += child.to_taskjuggler_language()
        else:
            if self.effort:
                attributes += "    effort %sh\n" % self.effort
            if self.assignee:
                attributes += "    allocate %s\n" % self.assignee

        output = u"""\
task %(id)s '%(name)s' {
%(attributes)s}
"""     % dict(id=self.taskjuggler_id,
               name=quoted_string(self.name),
               attributes=attributes)

        return output

def quoted_string(s):
    s = s.replace('\\', '\\\\').replace("'", "\\'")
    # Hack for report display: text is not escaped in the HTML output
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt')
    return s
