
from ConfigParser import ConfigParser
from copy import copy

from mongoDB.config import DEFAULT_DB_CONFIG

DB_OPTS = 'dbOptions'
QSERVE_OPTS = 'qServeOptions'

DEFAULT_QSERVE_CONFIG = { 'host':'0.0.0.0' , 'port':6060 }

def default_configs():
    return { 'db':DEFAULT_DB_CONFIG, 'qserve':DEFAULT_QSERVE_CONFIG }

def get_configs(ini_file):
    # Retrieve configurations
    conf = ConfigParser()
    conf.read(ini_file)

    db_config = copy(DEFAULT_DB_CONFIG)
    # Parse DB configurations
    for db_opt in conf.options(DB_OPTS):
        if db_opt in ['name','host','port']:
            db_config[db_opt] = conf.get(DB_OPTS, db_opt)

    qs_config = copy(DEFAULT_QSERVE_CONFIG)
    # Parse Query Serice configurations
    for qs_opt in conf.options(QSERVE_OPTS):
        if qs_opt in ['host','port']:
            qs_config[qs_opt] = conf.get(QSERVE_OPTS, qs_opt)
 
    return { 'db':db_config, 'qserve':qs_config }


