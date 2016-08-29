
import os
import logging

from pymongo import MongoClient, DESCENDING

from bson.objectid import ObjectId

from config import DEFAULT_DB_CONFIG
# from ops import get_db, COLL_REPOS, COLL_BCOUNTS
from records import REPO, USER, HASH, BCOUNT

COLL_REPOS   = 'repos'
COLL_BCOUNTS = 'bcounts'
COLL_TEST    = 'test'

def get_db(config=DEFAULT_DB_CONFIG):
    if config['host'] == None and config['port'] == None:
        client = MongoClient()
    else:
        db_host = config['host'] if config['host'] != None else 'localhost'
        db_port = config['port'] if config['port'] != None else '27017'        
        client = MongoClient("mongodb://%s:%s" % (db_host,db_port))
    if config['user'] != None and config['pwd'] != None:
        client[config['name']].authenticate(config['user'], config['pwd'])
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

TOTAL_COMMIT_BUILDS   = 0
TOTAL_REPO_BUILDS     = 1
TOTAL_COMMIT_ATTEMPTS = 2
TOTAL_REPO_ATTEMPTS   = 3

# Count
def count_totals(count_type, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    if count_type in [TOTAL_COMMIT_BUILDS,TOTAL_REPO_BUILDS]:
        bcount_col = app_builder_db[COLL_BCOUNTS]
        it = bcount_col.find( { 'bcount' : { '$gt' : 0 } } )
        if count_type == TOTAL_COMMIT_BUILDS:
            total = 0
            for i in it:
                total += i['bcount']
            return total
        else:
            return it.count()
    else:
        # TODO
        return 0 

# Get repository data by id
def get_repo_data_by_id(oid, config=DEFAULT_DB_CONFIG):
    resp = get_repo_data_by_ids([oid], config=config)
    if len(resp) > 0:
       return resp[0]
    else:
       return None

def show_db_connect_params(config=DEFAULT_DB_CONFIG):
    host = config['host']
    port = config['port']
    if host == None:
        host = "127.0.0.1"
    if port == None:
        port = "27017"
    msg = "MongoDB %s @ %s:%s" % (config['name'],host,port)
    if config['user'] and config['pwd']:
        msg += " with auth (%s,%s)" % (config['user'],config['pwd'])
    return msg

def ping_db(config=DEFAULT_DB_CONFIG):
    try:
        db = get_db(config=config)
        test_key = "ping_%s" % os.getpid()
        db[COLL_TEST].insert_one( { 'ping': test_key } )
        db[COLL_TEST].find( { 'ping': test_key } ).count()
        db[COLL_TEST].delete_many( { 'ping': test_key } )
    except Exception, e:
        err_msg = 'Failed to connect to DB: %s' % show_db_connect_params(config=config)
        logging.error(err_msg, exc_info=True)
        print err_msg
        return False
    return True

