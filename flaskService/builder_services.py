
from os import path
import logging

from config import get_configs, default_configs, load_configs, load_configs_with_cmd_line_overrides
from build_logging import setup_logging

from redisJobQueue.config import DEFAULT_REDIS_CONFIG
from redisJobQueue.ops import get_redis, bpop_job, pop_admin_task, BUILDER_TERMINATE
from appbuilder.app_builder import run_builder, RepoProcessor
from mongoDB.ops import get_or_create_new_repo_record, update_repo_record

ini_file_path = 'app_builder.ini'
CONFIGS = load_configs_with_cmd_line_overrides() # load_configs( ini_file_path )

def db_get_repo_record(user_name, repo_name, hash_id):
    return get_or_create_new_repo_record(user_name, repo_name, hash_id=hash_id, config=CONFIGS['db'])

def db_update_repo_record(repo_record, stat, snippet, app_updates):
    return update_repo_record(repo_record, CONFIGS['build']['name'], stat, snippet, app_updates, config=CONFIGS['db'])

def builder_loop():

    msg = '''
================================================================================
Running builder daemon, connected to redis@%s:%s , listening to builder admin channel '%s' and job queue '%s'
================================================================================''' % (CONFIGS['redis']['host'],CONFIGS['redis']['port'],CONFIGS['redis']['builder'],CONFIGS['redis']['jobs'])

    # Setup redis client
    rd = get_redis( config=CONFIGS['redis'] )
    
    try:
        rd.ping()
    except Exception, e:
        logging.error('Cannot connect to Redis server!', exc_info=True)
        print "Failed to connect to Redis. Did you forget to start Redis @ %s:%s?" % (CONFIGS['redis']['host'],CONFIGS['redis']['port'])
        return None

    # Setup a repository processor
    repoProcessor = RepoProcessor(CONFIGS['build']['workdir'], CONFIGS['build']['archivedir'])
    repoProcessor.setDBOps(db_get_repo_record, db_update_repo_record)

    print msg

    # Start the daemon routine.
    terminated = False
    while True:
       new_job = None
       try:
           new_job = bpop_job(timeout=5, redis_store=rd, config=CONFIGS['redis'])
       except Exception, e:
           logging.error('Exception occurred in job queue!', exc_info=True)

       # Check kill signal
       try:
           admin_msg = pop_admin_task(redis_store=rd, config=CONFIGS['redis'])
           if admin_msg != None:
               if admin_msg['code'] == BUILDER_TERMINATE:
                   terminated = True
       except Exception, e:
           logging.error('Exception occurred in admin channel!', exc_info=True)

       # process a job
       if new_job != None:
           if new_job['hash'] == None:
               repo = (new_job['user'],new_job['repo'])
           else:
               repo = (new_job['user'],new_job['repo'],new_job['hash'])
           try:
               repoProcessor.processFromDB( [repo], force_build=new_job['force'], remove=new_job['remove'] )
           except Exception, e:
               logging.error('Fatal exception occurred while processing repo: %s %s %s' % (new_job['user'],new_job['repo'],new_job['hash']), exc_info=True)    
       
           print msg

       # If kill signal was received, stop
       if terminated:
           print "Terminating ..."
           break

if __name__ == "__main__":
    setup_logging( CONFIGS, process_name = CONFIGS['build']['name'] )
    builder_loop()


