
from redis import StrictRedis
from json import dumps, loads

from config import DEFAULT_REDIS_CONFIG

def get_redis(config=DEFAULT_REDIS_CONFIG):
    return StrictRedis(host=config['host'], port=config['port'], db=config['db'])

# Yes.. its currently serializing JSON. Quick and simple solution
# TODO: Satisfy Protobuf scums by changing to Protobufs perhaps? 

def push_job(user_name, repo_name, hash_id=None, force_build=False, remove=True, redis_store=None, config=DEFAULT_REDIS_CONFIG):
    if redis_store == None:
        redis_store = get_redis(config=config)
    job = { 'user':user_name, 'repo':repo_name, 'hash':hash_id, 'force':force_build, 'remove':remove }
    redis_store.lpush( config['jobs'], dumps(job) )

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
       print data
       return loads( data )
    else:
       return None


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

