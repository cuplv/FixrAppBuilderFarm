from flask import Flask, request, jsonify

from bson.json_util import dumps
from bson.objectid import ObjectId

# from mongoDB.test import get_db
from mongoDB.query import get_repo_data, get_top_N_buildable_repo_data, get_repo_data_by_ids
from mongoDB.config import DEFAULT_DB_CONFIG

from os import path
from config import get_configs, default_configs, DEFAULT_QSERVE_CONFIG

app = Flask(__name__)

ini_file_path = 'app_builder.ini'
if path.exists(ini_file_path):
   CONFIGS = get_configs(ini_file_path)
else:
   CONFIGS = default_configs()

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



if __name__ == "__main__":
    app.run(host=CONFIGS['qserve']['host'], port=CONFIGS['qserve']['port'])

