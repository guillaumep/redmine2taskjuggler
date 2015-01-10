from ConfigParser import RawConfigParser

_conf = None
CONFIG_FILE = 'redmine2taskjuggler.conf'

def get_config():
    global _conf
    if _conf:
        return _conf

    confparser = RawConfigParser()
    if not confparser.read(CONFIG_FILE):
        raise Exception("Configuration file %s cannot be read." % CONFIG_FILE)

    _conf = {}
    for section in confparser.sections():
        _conf[section] = {}
        for option in confparser.options(section):
            _conf[section][option] = confparser.get(section, option)
    return _conf
