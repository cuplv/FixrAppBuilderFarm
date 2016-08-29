
from ConfigParser import ConfigParser
from copy import copy

DB_OPTS = 'dbOptions'

DEFAULT_DB_CONFIG = { 'name':'app_builder_db', 'host':None, 'port':None, 'user':None, 'pwd':None }

def get_configs(ini_file):
    db_config = copy(DEFAULT_DB_CONFIG)
    # Retrieve and parse DB configurations
    conf = ConfigParser(ini_file)
    for db_opt in conf.options(DB_OPTS):
        if db_opt in ['name','host','port']:
            db_config[db_opt] = conf.get(DB_OPTS, db_opt)
    return db_config
