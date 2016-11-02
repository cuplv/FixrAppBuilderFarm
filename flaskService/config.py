
from ConfigParser import ConfigParser
from copy import copy
from os import path
import optparse

from mongoDB.config import DEFAULT_DB_CONFIG
from redisJobQueue.config import DEFAULT_REDIS_CONFIG, REDIS_OPTS

DB_OPTS = 'dbOptions'
QSERVE_OPTS = 'qServeOptions'
BUILD_OPTS = 'buildOptions'
LOG_OPTS = 'logOptions'

FILE_LOGGING = 'file'
GRAY_LOGGING = 'graylog'

DEFAULT_QSERVE_CONFIG = { 'host':'0.0.0.0' , 'port':6060, 'name':'query1' }
DEFAULT_BUILDER_CONFIG = { 'workdir':'work', 'storeidx':0, 'archivehost':None, 'archivedir':'/data', 'name':'builder1'
                         , 'gradlefarmpath':'/data/gradle_farm', 'removework':True }
DEFAULT_LOG_CONFIG = { 'logtype': FILE_LOGGING, 'filename': 'log', 'host':'0.0.0.0', 'port':12201 }

def default_configs():
    return { 'db':DEFAULT_DB_CONFIG, 'redis':DEFAULT_REDIS_CONFIG, 'qserve':DEFAULT_QSERVE_CONFIG, 'build':DEFAULT_BUILDER_CONFIG, 'log':DEFAULT_LOG_CONFIG }

def get_configs(ini_file):
    # Retrieve configurations
    conf = ConfigParser()
    conf.read(ini_file)

    db_config = copy(DEFAULT_DB_CONFIG)
    # Parse DB configurations
    for db_opt in conf.options(DB_OPTS):
        if db_opt in ['name','host','port','user','pwd']:
            db_config[db_opt] = conf.get(DB_OPTS, db_opt)
 
    rd_config = copy(DEFAULT_REDIS_CONFIG)
    # Parse Redis Job Queue configurations
    for rd_opt in conf.options(REDIS_OPTS):
        if rd_opt in ['host','port', 'db', 'jobs', 'builder','pwd','failed']:
            rd_config[rd_opt] = conf.get(REDIS_OPTS, rd_opt)

    qs_config = copy(DEFAULT_QSERVE_CONFIG)
    # Parse Query Service configurations
    for qs_opt in conf.options(QSERVE_OPTS):
        if qs_opt in ['host','port','name']:
            qs_config[qs_opt] = conf.get(QSERVE_OPTS, qs_opt)

    bd_config = copy(DEFAULT_BUILDER_CONFIG)
    # Parse Builder Service configurations
    for bd_opt in conf.options(BUILD_OPTS):
        if bd_opt in ['workdir','storeidx','archivehost','archivedir','name','gradlefarmpath']:
            bd_config[bd_opt] = conf.get(BUILD_OPTS, bd_opt)
        if bd_opt == 'removework':
            rmwork = conf.get(BUILD_OPTS, bd_opt)
            bd_config[bd_opt] = rmwork in ['true','True'] 

    log_config = copy(DEFAULT_LOG_CONFIG)
    # Parse Logging configurations
    for log_opt in conf.options(LOG_OPTS):
        # print log_opt
        if log_opt in ['filename','host','port']:
            log_config[log_opt] = conf.get(LOG_OPTS, log_opt)
        if log_opt == 'logtype':
            logType = conf.get(LOG_OPTS, log_opt)
            if logType in ['graylog','Graylog','grayLog','GrayLog']: 
                # print "gray logging"
                log_config[log_opt] = GRAY_LOGGING
            else:
                # print "file logging"
                log_config[log_opt] = FILE_LOGGING
                
    return { 'db':db_config, 'redis':rd_config, 'qserve':qs_config, 'build':bd_config, 'log':log_config }



def load_configs(ini_file_path):
    if path.exists(ini_file_path):
       return get_configs(ini_file_path)
    else:
       return default_configs()

def load_configs_with_cmd_line_overrides():
    p = optparse.OptionParser()
    p.add_option('-i', '--ini', help=".ini file to use", default="app_builder.ini")
    p.add_option('-n', '--name', help="name of this instance")
    p.add_option('-w', '--work', help="name of working directory")
    
    opts, args = p.parse_args()
    configs = load_configs(opts.ini)
    if opts.name != None:
        configs['build']['name']  = opts.name
        configs['qserve']['name'] = opts.name
        configs['redis']['builder']  = opts.name
    if opts.work != None:
        configs['build']['workdir'] = opts.work

    return configs



