
from pymongo import MongoClient, DESCENDING

from bson.objectid import ObjectId

from config import DEFAULT_DB_CONFIG
# from ops import get_db, COLL_REPOS, COLL_BCOUNTS
from records import REPO, USER, HASH, BCOUNT

COLL_REPOS   = 'repos'
COLL_BCOUNTS = 'bcounts'

def get_db(config=DEFAULT_DB_CONFIG):
    if config['host'] == None and config['port'] == None:
        client = MongoClient()
    else:
        db_host = config['host'] if config['host'] != None else 'localhost'
        db_port = config['port'] if config['port'] != None else '27017'        
        client = MongoClient("mongodb://%s:%s" % (db_host,db_port))
    return client[config['name']]

# Preprocess the output of the find operation. Specific, we want to
#      i. extract string component of mongoDB ID objects, found in _id field.
#     ii. 'force' execution of the find operation.
def preprocess_records(find_output):
    response = []
    for record in find_output:
        record['_id'] = record['_id'].__str__()
        response.append( record )
    return response

# Standard query for repository data
def get_repo_data(user_name=None, repo_name=None, hash_id=None, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    query = {}
    if user_name != None:
       query[USER] = user_name
    if repo_name != None:
       query[REPO] = repo_name 
    if hash_id != None:
       query[HASH] = hash_id
    return preprocess_records( app_builder_db[COLL_REPOS].find(query) )

# Get top n most buildable repository data
def get_top_N_buildable_repo_data(n=50, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    bcount_col = app_builder_db[COLL_BCOUNTS]    
    return preprocess_records( bcount_col.find().sort([(BCOUNT,DESCENDING)]).limit(n) )

# Get repository data by ids
def get_repo_data_by_ids(oids, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    repo_col = app_builder_db[COLL_REPOS]
    # query = { '_id': { '$in': map(lambda oid: ObjectId(oid), oids) } }
    query = { '_id': ObjectId(oids[0]) }
    # print query
    return preprocess_records( repo_col.find(query) )

# Get repository data by id
def get_repo_data_by_id(oid, config=DEFAULT_DB_CONFIG):
    resp = get_repo_data_by_ids([oid], config=config)
    if len(resp) > 0:
       return resp[0]
    else:
       return None

