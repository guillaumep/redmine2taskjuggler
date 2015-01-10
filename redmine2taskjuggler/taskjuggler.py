class Resource:
    def __init__(self, id, name, email=None):
        self.id = id
        self.name = name
        self.email = email

    def to_taskjuggler_language(self):
        output = u"""\
resource {0.id} \"{0.name}\"
{{ email \"{0.email}\" }}\
""".format(self)
        return output
