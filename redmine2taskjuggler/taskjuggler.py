class Resource:
    def __init__(self, id, name, email=None):
        self.id = id
        self.name = name
        self.email = email

    def to_taskjuggler_language(self):
        output = u"""\
resource %(id)s '%(name)s'
{ email '%(email)s' }
"""     % dict(id=self.id,
               name=quoted_string(self.name),
               email=self.email)
        return output

class Task:
    def __init__(self, id, name, effort, assignee=None):
        self.id = id
        self.name = name
        self.effort = effort # in hours
        self.assignee = assignee

    def to_taskjuggler_language(self):
        attributes = ""
        if self.effort:
            attributes += "    effort %sh\n" % self.effort
        if self.assignee:
            attributes += "    allocate %s\n" % self.assignee

        output = u"""\
task %(id)s '%(name)s' {
%(attributes)s}
"""     % dict(id=self.id,
               name=quoted_string(self.name),
               attributes=attributes)

        return output

def quoted_string(s):
    s = s.replace('\\', '\\\\').replace("'", "\\'")
    # Hack for report display: text is not escaped in the HTML output
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt')
    return s
