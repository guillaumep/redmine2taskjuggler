import string
from redmine2taskjuggler.config_reader import get_config

IDENTATION = 4

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
        return str(self.id)

    def to_taskjuggler_language(self):
        output = u"""\
resource %(id)s '%(name)s'
{ email '%(email)s' }
"""     % dict(id=self.taskjuggler_id,
               name=quoted_string(self.name),
               email=self.email)
        return output

class Task:
    def __init__(self, id, name, effort, assignee=None, priority=None,
                 scheduling=None, end_date=None):
        self.id = id
        self.name = name
        self.effort = effort # in hours
        self.assignee = assignee
        self.priority = priority
        self.scheduling = scheduling
        self.end_date = end_date
        self.parent = None
        self.children = []

    @property
    def taskjuggler_id(self):
        return self.id

    def to_taskjuggler_language(self, depth=1):
        attributes = ""
        ident = ' ' * (depth + 1) * IDENTATION
        if self.priority:
            attributes += "%spriority %s\n" % (ident, self.priority)
        if self.scheduling:
            attributes += "%sscheduling %s\n" % (ident, self.scheduling)
        if self.children:
            for child in self.children:
                attributes += child.to_taskjuggler_language(depth=depth + 1)
        else:
            if self.effort:
                attributes += "%seffort %sh\n" % (ident, self.effort)
            if self.assignee:
                attributes += "%sallocate %s\n" % (ident, self.assignee)
            if self.end_date:
                attributes += "%send %s\n" % (ident, self.end_date.strftime('%Y-%m-%d'))

        output = u"""\
%(ident)stask %(id)s '%(name)s' {
%(attributes)s%(ident)s}
"""     % dict(id=self.taskjuggler_id,
               name=quoted_string(self.name),
               attributes=attributes,
               ident=' ' * depth * IDENTATION)

        return output

def quoted_string(s):
    s = s.replace('\\', '\\\\').replace("'", "\\'")
    # Hack for report display: text is not escaped in the HTML output
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt')
    return s
