from redmine import Redmine
from redmine2taskjuggler.config_reader import get_config

_redmine = None

def get_redmine():
    global _redmine
    if _redmine:
        return _redmine
    config = get_config()
    _redmine = Redmine(config['redmine']['url'], key=config['redmine']['api_key'])
    return _redmine
