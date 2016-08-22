
from pymongo import MongoClient, HASHED, DESCENDING

from records import USER, REPO, HASH, BCOUNT
from config import DEFAULT_DB_CONFIG

# APP_BUILDER_DB_NAME = 'app_builder_db'

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

def init_db(config=DEFAULT_DB_CONFIG):
    # client = MongoClient()
    # app_builder_db = client[APP_BUILDER_DB_NAME]
    app_builder_db = get_db(config=config) 
    # Create Indices for main repository collection
    repo_data = app_builder_db[COLL_REPOS]
    repo_data.create_index([(USER, HASHED)])
    repo_data.create_index([(REPO, HASHED)])
    repo_data.create_index([(HASH, HASHED)])
    # Create Indices for aux build count collection
    bcount_data = app_builder_db[COLL_BCOUNTS]
    bcount_data.create_index([(USER, HASHED)])
    bcount_data.create_index([(REPO, HASHED)])
    bcount_data.create_index([(BCOUNT, DESCENDING)])

def clear_db(config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    app_builder_db[COLL_REPOS].drop()
    app_builder_db[COLL_BCOUNTS].drop()

def add_repo_records(repo_records, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    repo_data = app_builder_db[COLL_REPOS]
    repo_data.insert_many( repo_records )

def add_bcount_records(bcount_records, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    bcount_data = app_builder_db[COLL_BCOUNTS]
    bcount_data.insert_many( bcount_records )


