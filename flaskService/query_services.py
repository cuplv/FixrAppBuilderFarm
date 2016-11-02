from flask import Flask, request, jsonify

from bson.json_util import dumps
from bson.objectid import ObjectId

# from mongoDB.test import get_db
from mongoDB.query import ping_db, show_db_connect_params, get_repo_data, get_top_N_buildable_repo_data, get_repo_data_by_ids, count_totals, count_all_totals, get_repo_builds_with_fixes, get_repo_build_counts, TOTAL_COMMIT_BUILDS, TOTAL_REPO_BUILDS, TOTAL_COMMIT_ATTEMPTS, TOTAL_REPO_ATTEMPTS
from mongoDB.config import DEFAULT_DB_CONFIG

from redisJobQueue.ops import ping_redis, num_of_jobs

from os import path
from config import get_configs, default_configs, load_configs, DEFAULT_QSERVE_CONFIG, load_configs_with_cmd_line_overrides

from build_logging import setup_logging

ini_file_path = '/eval/FixrAppBuilderFarm/flaskService/app_builder.ini'
# CONFIGS = load_configs_with_cmd_line_overrides() # load_configs( ini_file_path )

app = Flask(__name__)

@app.route("/repo/")
def query_repo():
    CONFIGS = load_configs(ini_file_path)
    user = request.args.get('user')
    repo = request.args.get('repo')
    hash_id = request.args.get('hash')
    raw_stats = request.args.get('stats')
    if raw_stats != None:
        stats = []
        for raw_stat in raw_stats.split(','):
            stat = None
            if raw_stat in ['ps','passed','built']:
                stat = 'PS'
            elif raw_stat in ['fl','failed']:
                stat = 'FL'
            elif raw_stat in ['ex','except']:
                stat = 'EX'
            elif raw_stat in ['sk','skipped']:
                stat = 'SK'
            elif raw_stat in ['ko','timedout']:
                stat = 'KO'
            if stat != None:
                stats.append( stat )
    else:
        stats = []
    page  = request.args.get('page')
    page  = int(page) if page != None else 0
    per_page = request.args.get('per_page')
    per_page = int(per_page) if per_page != None else 0    
    resp = get_repo_data( user, repo, hash_id, stats=stats, page=page, per_page=per_page, config=CONFIGS['db'] )
    return jsonify( results=resp )

@app.route("/builds/")
def query_builds_with_fixes():
    CONFIGS = load_configs(ini_file_path)
    user = request.args.get('user')
    repo = request.args.get('repo')
    hash_id = request.args.get('hash')
    counts = request.args.get('counts')
    if counts in ['True','true','Yes','yes','1']:
       resp = get_repo_build_counts(user, repo, config=CONFIGS['db'])
    else:
       fix_applied = request.args.get('fix_applied')
       if fix_applied in ['True','true','Yes','yes','1']:
           resp = get_repo_builds_with_fixes(user, repo, hash_id, config=CONFIGS['db'])
       else:
           resp = get_repo_data(user, repo, hash_id, stats=['PS'], config=CONFIGS['db'])
    return jsonify( results=resp )
    
@app.route("/top/")
def query_top_builable():
    CONFIGS = load_configs(ini_file_path)
    n = int( request.args.get('n') )
    resp = get_top_N_buildable_repo_data( n=n, config=CONFIGS['db'] )
    return jsonify( result=resp )

@app.route("/id/")
def query_id():
    CONFIGS = load_configs(ini_file_path)
    oid = request.args.get('id')
    resp = get_repo_data_by_ids([oid], config=CONFIGS['db'])
    return jsonify( result=resp )

@app.route("/ids/")
def query_ids():
    CONFIGS = load_configs(ini_file_path)
    oids = request.args.get('ids')
    resp = get_repo_data_by_ids(oids.split(','), config=CONFIGS['db'])
    return jsonify( result=resp )

@app.route("/count/commit/builds/")
def query_count_commit_builds():
    CONFIGS = load_configs(ini_file_path)
    count = count_totals( TOTAL_COMMIT_BUILDS, config=CONFIGS['db'] )
    return jsonify( total=count )

@app.route("/count/repo/builds/")
def query_count_repo_builds():
    CONFIGS = load_configs(ini_file_path)
    count = count_totals( TOTAL_REPO_BUILDS, config=CONFIGS['db'] )
    return jsonify( total=count )

@app.route("/count/all/")
def query_count_alls():
    CONFIGS = load_configs(ini_file_path)
    counts = count_all_totals( config=CONFIGS['db'] )
    jobs_left = num_of_jobs(config=CONFIGS['redis'])
    counts['in_queue'] = jobs_left 
    return jsonify( results=counts )

if __name__ == "__main__":
    setup_logging( CONFIGS, process_name = CONFIGS['qserve']['name'] )
    if ping_db(config=CONFIGS['db']) and ping_redis(config=CONFIGS['redis']):
         app.run(host=CONFIGS['qserve']['host'], port=CONFIGS['qserve']['port'])
    else:
         print "terminating ..."

