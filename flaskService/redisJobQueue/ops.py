
import os
import logging

from redis import StrictRedis
from json import dumps, loads

from config import DEFAULT_REDIS_CONFIG

def get_redis(config=DEFAULT_REDIS_CONFIG):
    if config['pwd'] == None:
        return StrictRedis(host=config['host'], port=config['port'], db=config['db'])
    else:
        return StrictRedis(host=config['host'], port=config['port'], db=config['db'], password=config['pwd'])

# Yes.. its currently serializing JSON. Quick and simple solution
# TODO: Satisfy Protobuf scums by changing to Protobufs perhaps? 

def push_job(user_name, repo_name, hash_id=None, force_build=False, remove=True, redis_store=None, config=DEFAULT_REDIS_CONFIG):
    if redis_store == None:
        redis_store = get_redis(config=config)
    job = { 'user':user_name, 'repo':repo_name, 'hash':hash_id, 'force':force_build, 'remove':remove }
    redis_store.lpush( config['jobs'], dumps(job) )

def push_failed_job(user_name, repo_name, hash_id, force_build=False, remove=True, redis_store=None, config=DEFAULT_REDIS_CONFIG):
    if redis_store == None:
        redis_store = get_redis(config=config)
    job = { 'user':user_name, 'repo':repo_name, 'hash':hash_id, 'force':force_build, 'remove':remove }
    redis_store.lpush( config['failed'], dumps(job) )

def pop_job(redis_store=None, config=DEFAULT_REDIS_CONFIG):
    if redis_store == None:
        redis_store = get_redis(config=config)
    data = redis_store.lpop( config['jobs'] )
    return loads( data ) if data != None else None

def bpop_job(timeout=0, redis_store=None, config=DEFAULT_REDIS_CONFIG):
    if redis_store == None:
        redis_store = get_redis(config=config)
    resp = redis_store.blpop( config['jobs'], timeout=timeout )
    if resp != None:
       _, data = resp
       # print data
       return loads( data )
    else:
       return None

def show_redis_connect_params(config=DEFAULT_REDIS_CONFIG, verbose=False):
    host = config['host']
    port = config['port']
    if host == None:
        host = "127.0.0.1"
    if port == None:
        port = "6379"
    msg = "Redis @ %s:%s" % (host,port)
    if config['pwd'] != None:
        msg += " with auth \'%s\'" % config['pwd']
    if verbose:
        msg += "\n   Fetching Jobs from \'%s\'" % config['jobs']
        msg += "\n   Listening for admin tasks from \'%s\'" % config['builder']
    return msg

def ping_redis(config=DEFAULT_REDIS_CONFIG):
    try:
        rd = get_redis(config=config)
        test_key = "ping_%s" % os.getpid()
        rd.lpush( test_key, -1)
        rd.lpop( test_key )
    except Exception, e:
        err_msg = 'Failed to connect to Redis server: %s' % show_redis_connect_params(config=config)
        logging.error(err_msg, exc_info=True)
        print err_msg
        return False
    return True

BUILDER_TERMINATE = -1

# Currently just supports terminate.

def push_admin_task(admin_code, args=None, redis_store=None, config=DEFAULT_REDIS_CONFIG):
    if redis_store == None:
        redis_store = get_redis(config=config)
    task = { 'code':admin_code }
    if args != None:
         task['args'] = args
    redis_store.lpush( config['builder'], dumps(task) )

def pop_admin_task(redis_store=None, config=DEFAULT_REDIS_CONFIG):
    if redis_store == None:
        redis_store = get_redis(config=config)
    data = redis_store.lpop( config['builder'] )
    return loads( data ) if data != None else None

