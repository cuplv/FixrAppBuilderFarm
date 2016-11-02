
import os
import sys
import json

from redisJobQueue.config import DEFAULT_REDIS_CONFIG
from redisJobQueue.ops import get_redis, push_job
from config import load_configs

def load_redis(input_json, force_build=False, remove=True, redis_store=None, config=DEFAULT_REDIS_CONFIG):
   if redis_store == None:
       redis_store = get_redis( config=config )
   with open(input_json, "r") as f:
      count = 0
      line = f.readline()
      while line != '':
         data = json.loads(line)
         push_job(data['user'], data['repo'], hash_id=data['hash'], dt_committed=data['dt_committed']
                 ,force_build=force_build, remove=remove, redis_store=redis_store, config=config)
         count += 1
         line = f.readline()
   print "Done! Added %s jobs" % count

if __name__ == "__main__":
   args = sys.argv
   if len(args) != 2:
       print "Usage: python %s <json file: 'repoName commitHash userName commitDate'>" % args[0]
       sys.exit(0)

   input_json = args[1]
   configs = load_configs('app_builder.ini')

   load_redis( input_json, config=configs['redis'] )


