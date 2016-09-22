
import os
import logging
import math

from pymongo import MongoClient, DESCENDING

from bson.objectid import ObjectId

from config import DEFAULT_DB_CONFIG
# from ops import get_db, COLL_REPOS, COLL_BCOUNTS
from records import REPO, USER, HASH, BUILDS

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
def get_repo_data(user_name=None, repo_name=None, hash_id=None, stats=[], page=0, per_page=0, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    query = {}
    if user_name != None:
       query[USER] = user_name
    if repo_name != None:
       query[REPO] = repo_name 
    if hash_id != None:
       query[HASH] = hash_id
    if len(stats) == 0:
       return preprocess_records( app_builder_db[COLL_REPOS].find(query, skip=page*per_page, limit=per_page) )
    else:
       query['builds.0.stat'] = { '$in':stats }
       return preprocess_records( app_builder_db[COLL_REPOS].find(query, skip=page*per_page, limit=per_page) )
       '''
       recs = []
       for rec in app_builder_db[COLL_REPOS].find(query, skip=skip, limit=limit):
           builds = rec['builds']
           if len(builds) > 0:
               if builds[0]['stat'] in stats:
                   recs.append( rec )
           else:
               if 'EX' in stats:
                   recs.append( rec )
       return preprocess_records( recs )
       '''

def get_repo_builds_with_fixes(user_name=None, repo_name=None, hash_id=None, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    query = {}
    if user_name != None:
       query[USER] = user_name
    if repo_name != None:
       query[REPO] = repo_name 
    if hash_id != None:
       query[HASH] = hash_id
    recs = []
    for rec in app_builder_db[COLL_REPOS].find(query):
       builds = rec['builds']
       add = False
       for build in builds:
           if build['stat'] == 'PS' and len(build['fix_applied']) > 0:
               add = True
               break
       if add:
            recs.append( rec )
    return preprocess_records( recs )

def get_repo_build_counts(user_name, repo_name, config=DEFAULT_DB_CONFIG):
    brecs = get_repo_data(user_name=user_name, repo_name=repo_name, stats=['PS'], config=config)
    total_commits = len( brecs )
    repo_dict = {}
    for brec in brecs:
        repo = "%s/%s" % (brec['user'],brec['repo'])
        repo_dict[repo] = ()
    total_repos = len( repo_dict.keys() )
    brecs = get_repo_builds_with_fixes(user_name=user_name, repo_name=repo_name, config=config)
    total_commits_wf = len( brecs )
    repo_dict = {}
    for brec in brecs:
        repo = "%s/%s" % (brec['user'],brec['repo'])
        repo_dict[repo] = ()
    total_repos_wf = len( repo_dict.keys() )

    commit_fix_rate = "fixed_commits / (all_commits) * 100 = %s%%" % roundoff(float(total_commits_wf) / (total_commits) * 100) 
    repo_fix_rate = "fixed_repos / (all_repos) * 100 = %s%%" % roundoff(float(total_repos_wf) / (total_repos) * 100) 

    return { 'all': { 'commits':total_commits, 'repos':total_repos }, 'fix_applied': { 'commits':total_commits_wf, 'repos':total_repos_wf } 
           , 'stat': { 'commit_fix_rate':commit_fix_rate, 'repo_fix_rate':repo_fix_rate } }

# Get top n most buildable repository data
def get_top_N_buildable_repo_data(n=50, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    bcount_col = app_builder_db[COLL_BCOUNTS]    
    return preprocess_records( bcount_col.find().sort([(BUILDS,DESCENDING)]).limit(n) )

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
        it = bcount_col.find( { 'builds' : { '$gt' : 0 } } )
        if count_type == TOTAL_COMMIT_BUILDS:
            total = 0
            for i in it:
                total += i['builds']
            return total
        else:
            return it.count()
    else:
        # TODO
        return 0 

def roundoff(v):
    return math.ceil(v*100)/100

def count_all_totals(config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    builds = 0
    fails = 0
    skips = 0
    excepts = 0
    timeouts = 0
    repos_built = 0
    repos_failed = 0
    repos_skipped = 0
    repos_except  = 0
    repos_timeout = 0
    repos_unknown = 0
    for rec in app_builder_db[COLL_BCOUNTS].find():
        rec_builds   = rec.get('builds', 0)
        rec_fails    = rec.get('fails', 0)
        rec_skips    = rec.get('skips', 0)
        rec_excepts  = rec.get('excepts', 0)
        rec_timeouts = rec.get('timeouts', 0)
        if rec_builds > 0:
            repos_built += 1
        else:
            stat = 'UN'
            if rec_skips > 0:
                stat = 'SK'
            if rec_fails > 0:
                stat = 'FL'
            if rec_excepts > 0:
                stat = 'EX'
            if rec_timeouts > 0:
                stat = 'KO'
            if stat == 'SK':
                repos_skipped += 1
            elif stat == 'FL':
                repos_failed += 1
            elif stat == 'EX':
                repos_except += 1
            elif stat == 'KO': 
                repos_timeout += 1
            else:
                repos_unknown += 1
 
        builds   += rec_builds
        fails    += rec_fails
        skips    += rec_skips
        excepts  += rec_excepts
        timeouts += rec_timeouts

    build_rate = "builds / (builds+fails) * 100 = %s%%" % roundoff(float(builds) / (builds+fails) * 100) 
    repo_build_rate = "builds / (builds+fails) * 100 = %s%%" % roundoff(float(repos_built) / (repos_built+repos_failed) * 100) 

    return { 'repos': { 'builds':repos_built, 'fails':repos_failed, 'skips':repos_skipped, 'excepts':repos_except, 'timeouts':repos_timeout
                      , 'unknown':repos_unknown, 'total': repos_built+repos_failed+repos_skipped+repos_except+repos_timeout+repos_unknown } 
           , 'commits' : { 'builds':builds, 'fails':fails, 'skips':skips, 'excepts':excepts, 'timeouts':timeouts
                         , 'total': builds + fails + skips + excepts + timeouts } 
           , 'stats': { 'commit_build_rate':build_rate, 'repo_build_rate':repo_build_rate } }

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

