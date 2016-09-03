
from os import path
import logging
import threading

from config import get_configs, default_configs, load_configs, load_configs_with_cmd_line_overrides
from build_logging import setup_logging

from redisJobQueue.config import DEFAULT_REDIS_CONFIG
from redisJobQueue.ops import ping_redis, show_redis_connect_params, get_redis, bpop_job, pop_admin_task, push_failed_job, BUILDER_TERMINATE
from appbuilder.app_builder import run_builder, RepoProcessor
from mongoDB.query import ping_db, show_db_connect_params
from mongoDB.ops import get_or_create_new_repo_record, update_records
from mongoDB.records import STAT_BUILD_PASSED

ini_file_path = 'app_builder.ini'
CONFIGS = load_configs_with_cmd_line_overrides() # load_configs( ini_file_path )

'''
def db_get_repo_record(user_name, repo_name, hash_id):
    return get_or_create_new_repo_record(user_name, repo_name, hash_id=hash_id, config=CONFIGS['db'])
'''
'''
def db_update_repo_record(repo_record, stat, snippet, app_updates):
    return update_repo_record(repo_record, CONFIGS['build']['name'], stat, snippet, app_updates, config=CONFIGS['db'])
'''

def input_reader(sig):
    while True:
        msg = raw_input('Awaiting signal :> ')
        if msg in ['stop','shutdown']:
             sig['terminate'] = True
             print "Termination key signal receiving, shutting down by end of next job ..."
             # return None 
        elif msg in ['cancel','abort']:
             sig['terminate'] = False
             print "Termination aborted, resuming operations."
        else:
             print "Unknown key strokes received: %s" % msg

def builder_loop():

    msg = '''
================================================================================
Builder Daemon %s in Action
%s
%s
================================================================================''' % (CONFIGS['build']['name'],show_redis_connect_params(CONFIGS['redis'],verbose=True),show_db_connect_params(CONFIGS['db']))
    
    '''
    try:
        rd.ping()
    except Exception, e:
        logging.error('Cannot connect to Redis server!', exc_info=True)
        print "Failed to connect to Redis. Did you forget to start Redis @ %s:%s?" % (CONFIGS['redis']['host'],CONFIGS['redis']['port'])
        return None
    '''
    # Ping Redis server and MongoDB. Proceed only if both connections are successfully established.
    if not ping_redis(config=CONFIGS['redis']) or not ping_db(config=CONFIGS['db']):
        print "terminating ..."
        return None

    rd = get_redis( config=CONFIGS['redis'] )

    # Setup a repository processor
    repoProcessor = RepoProcessor(CONFIGS['build']['workdir'], CONFIGS['build']['archivedir'], ext_archive=CONFIGS['build']['archivehost']
                                 ,gradle_farm=CONFIGS['build']['gradlefarmpath'])
    # repoProcessor.setDBOps(db_get_repo_record, db_update_repo_record)

    print msg

    sig = { 'terminate':False }
    td = threading.Thread(target=input_reader, args=(sig,))
    td.daemon = True
    td.start()
  
    # Start the daemon routine.
    terminated = False
    while True:
       new_job = None
       job_failed = False
       try:
           new_job = bpop_job(timeout=5, redis_store=rd, config=CONFIGS['redis'])
       except Exception, e:
           logging.error('Exception occurred in job queue!', exc_info=True)
           if not ping_redis(config=CONFIGS['redis']):
               print "terminating ..."
               return None

       # Check kill signal from redis
       try:
           admin_msg = pop_admin_task(redis_store=rd, config=CONFIGS['redis'])
           if admin_msg != None:
               if admin_msg['code'] == BUILDER_TERMINATE:
                   terminated = True
       except Exception, e:
           logging.error('Exception occurred in redis admin channel!', exc_info=True)

       # Check kill signal from keyboard
       try:
           if sig['terminate']:
               terminated = True
       except Exception, e:
           logging.error('Exception occurred checking key input!', exc_info=True)

       # process a job
       if new_job != None:
           user_name = new_job['user']
           repo_name = new_job['repo']
           hash_id   = new_job['hash'] if new_job['hash'] != None else "head"
           dt_committed = new_job['dt_committed'] 

           try:
               repo_rec, created, was_succ = get_or_create_new_repo_record(user_name, repo_name, store_loc=0, hash_id=hash_id, dt_committed=dt_committed, config=CONFIGS['db'])
           except Exception, e:
               logging.error('Fatal exception occurred while extracting repo records: %s %s %s' % (user_name, repo_name, hash_id), exc_info=True)    
               job_failed = True

           bres = None
           try:
               if was_succ and not new_job['force']:
                   logging.info("Already built, ignoring job: %s %s %s" % (user_name,repo_name,hash_id))
               else:  
                   bres = repoProcessor.processFromDB(user_name, repo_name, hash_id=hash_id, remove=new_job['remove'] )
                   job_failed = bres['build_stat'] != STAT_BUILD_PASSED
           except Exception, e:
               logging.error('Fatal exception occurred while processing repo: %s %s %s' % (user_name, repo_name, hash_id), exc_info=True)    
               job_failed = True

           if bres != None:
               # Start uploading the build meta-data into MongoDB
               try:
                   update_records(CONFIGS['build']['name'], repo_rec, bres, config=CONFIGS['db'])
               except Exception, e:
                   logging.error('Fatal exception occurred while uploading meta-data to mongoDB: %s %s %s'  % (user_name, repo_name, hash_id), exc_info=True)    
                   job_failed = True 

           if job_failed:
               if bres != None:
                   fail_stat = bres['build_stat']
               else:
                   fail_stat = 'EX'
               push_failed_job(user_name, repo_name, hash_id, dt_committed=dt_committed, force_build=False, remove=True, fail_stat=fail_stat, config=CONFIGS['redis'])

           print msg

       # If kill signal was received, stop
       if terminated:
           print "Terminating ..."
           break

if __name__ == "__main__":
    setup_logging( CONFIGS, process_name = CONFIGS['build']['name'] )
    builder_loop()


