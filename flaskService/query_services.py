from flask import Flask, request, jsonify

from bson.json_util import dumps
from bson.objectid import ObjectId

# from mongoDB.test import get_db
from mongoDB.query import ping_db, show_db_connect_params, get_repo_data, get_top_N_buildable_repo_data, get_repo_data_by_ids, count_totals, TOTAL_COMMIT_BUILDS, TOTAL_REPO_BUILDS, TOTAL_COMMIT_ATTEMPTS, TOTAL_REPO_ATTEMPTS
from mongoDB.config import DEFAULT_DB_CONFIG

from os import path
from config import get_configs, default_configs, load_configs, DEFAULT_QSERVE_CONFIG, load_configs_with_cmd_line_overrides

from build_logging import setup_logging

app = Flask(__name__)

ini_file_path = 'app_builder.ini'
CONFIGS = load_configs_with_cmd_line_overrides() # load_configs( ini_file_path )

@app.route("/repo/")
def query_repo():
    user = request.args.get('user')
    repo = request.args.get('repo')
    hash_id = request.args.get('hash')
    resp = get_repo_data( user, repo, hash_id, config=CONFIGS['db'] )
    return jsonify( results=resp )

@app.route("/top/")
def query_top_builable():
    n = int( request.args.get('n') )
    resp = get_top_N_buildable_repo_data( n=n, config=CONFIGS['db'] )
    return jsonify( result=resp )

@app.route("/id/")
def query_id():
    oid = request.args.get('id')
    resp = get_repo_data_by_ids([oid], config=CONFIGS['db'])
    return jsonify( result=resp )

@app.route("/ids/")
def query_ids():
    oids = request.args.get('ids')
    resp = get_repo_data_by_ids(oids.split(','), config=CONFIGS['db'])
    return jsonify( result=resp )

@app.route("/count/commit/builds/")
def query_count_commit_builds():
    count = count_totals( TOTAL_COMMIT_BUILDS, config=CONFIGS['db'] )
    return jsonify( total=count )

@app.route("/count/repo/builds/")
def query_count_repo_builds():
    count = count_totals( TOTAL_REPO_BUILDS, config=CONFIGS['db'] )
    return jsonify( total=count )

if __name__ == "__main__":
    setup_logging( CONFIGS, process_name = CONFIGS['qserve']['name'] )
    if ping_db(config=CONFIGS['db']):
         app.run(host=CONFIGS['qserve']['host'], port=CONFIGS['qserve']['port'])
    else:
         print "terminating ..."

