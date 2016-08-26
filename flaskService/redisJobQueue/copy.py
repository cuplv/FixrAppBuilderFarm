
import json

from config import DEFAULT_REDIS_CONFIG
from ops import get_redis, push_job

def retrieve_history_json_and_load_redis(jsonfilename, force_build=False, remove=True, redis_store=None, config=DEFAULT_REDIS_CONFIG):
    if redis_store == None:
        redis_store = get_redis( config=config )
    with open(jsonfilename, "r") as f:
        line = f.readline()
        while line != '':
            for data in json.loads(line):
                user_name,repo_name = data['repo'].split("/")
                push_job(user_name, repo_name, hash_id=data['hash'], force_build=force_build, remove=remove, 
                         redis_store=redis_store, config=config)
                print "Added: %s  %s  %s" % (user_name,repo_name,data['hash'])
            line = f.readline()
    print "Done!"
