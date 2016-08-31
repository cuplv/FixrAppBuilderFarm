
import json
from datetime import datetime

from config import DEFAULT_REDIS_CONFIG
from ops import get_redis, push_job

# Date str format: "2014-05-13 09:38:56 +0530"
def get_epochtime_from_str(dt_str):
    dt = datetime.strptime(dt_str[:-6], '%Y-%m-%d %H:%M:%S')
    return int(dt.strftime('%s'))


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
                       dt_committed = get_epochtime_from_str( data['date'] )
                       push_job(user_name, repo_name, hash_id=data['hash'], dt_committed=dt_committed, force_build=force_build, remove=remove, 
                                redis_store=redis_store, config=config)
                       print "Added: %s  %s  %s" % (user_name,repo_name,data['hash'])
                   else:
                       break
                   commit_count += 1
                else:
                   skip_count += 1
            line = f.readline()
    print "Done!"


def count_repos_history_json(jsonfilename):
    with open(jsonfilename, "r") as f:
        line = f.readline()
        count = 0
        while line != '':
            count += 1
            line = f.readline()
    print "Number of Repos: %s" % count 


