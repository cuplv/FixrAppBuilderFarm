
from pymongo import MongoClient, HASHED, DESCENDING

from bson.objectid import ObjectId

from records import *
from query import *
from config import DEFAULT_DB_CONFIG

# APP_BUILDER_DB_NAME = 'app_builder_db'

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

'''
Retrieve repository records from DB. If it does not exist, create and new one and store that new record 
in the DB, and return it, with a boolean flag indicating if it was newly created.
'''
def get_or_create_new_repo_record(user_name, repo_name, store_loc=0, hash_id="head", config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    repo_col = app_builder_db[COLL_REPOS]
    # repo_records = get_repo_data(user_name, repo_name, hash_id=hash_id, config=config)
    query = { USER: user_name, REPO: repo_name, HASH:hash_id }
    repo_records = preprocess_records( repo_col.find(query) )
    if len(repo_records) > 0:
       repo_record = repo_records[0]
       build_recs = repo_record[BUILDS]
       if len(build_recs) > 0:
           was_succ = build_recs[0][STAT] == STAT_BUILD_PASSED
       else:
           was_succ = False
       return (repo_record, False, was_succ)
    else:
       # app_records = map(lambda app_name: new_app_record(app_name, []), app_names)
       repo_record = new_repo_record(user_name, repo_name, {}, [], store_loc=store_loc, hash_id=hash_id)
       result = repo_col.insert_one( repo_record )
       repo_record['_id'] = result.inserted_id.__str__()
       return (repo_record, True, False)

'''
Updating repo records:
    old_repo_rec     - The repository record to be updated
    app_build_updates - Dictionary of mappings app_name: build_record, to be added
'''
def update_repo_record(old_repo_rec, stat, snippet, app_updates, config=DEFAULT_DB_CONFIG):

    def compare_build_recs(build_recs, build_rec):
        old_stat = 0
        if len(build_recs) > 0:
            old_stat = build_recs[0][STAT]
        if build_rec[STAT] > old_stat:
            return 1
        elif build_rec[STAT] == old_stat:
            return 0
        else:
            return -1

    # Process updates: Append build records, compute new changes to build counts,
    # and retrieve current epoch time.
    ## set_dict = { }

    '''
    app_dict = old_repo_rec[APPS]
    count_delta = 0
    count_updates = 0

    for app_name in app_build_updates:
        build_update = app_build_updates[app_name]
        build_rec = new_build_record(build_update['stat'], build_update['snippet'])
        if app_name in app_dict:
            build_recs = app_dict[app_name]
            count_delta += compare_build_recs(build_recs, build_rec)
            build_recs.insert(0, build_rec)
        else:
            count_delta += compare_build_recs([], build_rec)
            app_dict[app_name] = [build_rec]
        count_updates += 1
    '''

    build_recs = old_repo_rec[BUILDS]
    build_rec  = new_build_record(stat, snippet)
    delta      = compare_build_recs(build_recs, build_rec)

    now = get_epochtime_now()
    set_dict = { BUILDS: [build_rec] + build_recs, DT_MODIFIED: now }

    if len(app_updates) > 0:
        app_dict = old_repo_rec[APPS]
        for app_name in app_updates:
            src,cls,jar,apk = app_updates[app_name]
            app_dict[app_name] = new_app_record( src, cls, jar, apk )
        set_dict[APPS] = app_dict

    app_builder_db = get_db(config=config)
    repo_col = app_builder_db[COLL_REPOS]
    repo_col.update_one(
        { "_id": ObjectId(old_repo_rec['_id']) },
        { "$set": set_dict } # {  APPS: app_dict, DT_MODIFIED: now } }
    )
    bcount_col = app_builder_db[COLL_BCOUNTS]
    bcount_col.update_one(
        { USER:old_repo_rec[USER], REPO:old_repo_rec[REPO] },
        { "$inc": { BCOUNT:delta } },
        upsert = True
    )

    return delta

def test_modify(user_name="Leeloy Crap", repo_name="Dance the night away", app_names=["Funny", "Foo Bar"]):
     repo_rec, created = get_or_create_new_repo_record(user_name, repo_name)
     print "Created new entry: %s" % created
     app_build_updates = {}
     for app_name in app_names:
         app_build_updates[app_name] = new_build_record(STAT_BUILD_PASSED, "<blah blah blah>")
     counts = update_repo_record(repo_rec, app_build_updates)
     print "Build records added: %s" % counts


