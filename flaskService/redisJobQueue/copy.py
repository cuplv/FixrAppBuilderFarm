
import json

from config import DEFAULT_REDIS_CONFIG
from ops import get_redis, push_job

def retrieve_history_json_and_load_redis(jsonfilename, force_build=False, remove=True, skip_first=0, max_per_repo=5, redis_store=None, config=DEFAULT_REDIS_CONFIG):
    if redis_store == None:
        redis_store = get_redis( config=config )
    with open(jsonfilename, "r") as f:
        line = f.readline()
        while line != '':
            skip_count = 0
            commit_count = 0
            for data in json.loads(line):
                if skip_count >= skip_first:
                   if commit_count < max_per_repo:
                       user_name,repo_name = data['repo'].split("/")
                       push_job(user_name, repo_name, hash_id=data['hash'], force_build=force_build, remove=remove, 
                                redis_store=redis_store, config=config)
                       print "Added: %s  %s  %s" % (user_name,repo_name,data['hash'])
                   else:
                       break
                   commit_count += 1
                else:
                   skip_count += 1
            line = f.readline()
    print "Done!"
