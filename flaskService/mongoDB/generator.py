
from random import Random, getrandbits
from datetime import datetime

from ops import add_repo_records, add_bcount_records, get_db, COLL_REPOS, COLL_BCOUNTS
from config import DEFAULT_DB_CONFIG

from records import *

r = Random()

USER_NAMES = ['Ken', 'Sergio', 'Tom', 'Shawn', 'Evan', 'Edmund', 'Harry', 'Potter', 'John', 'Lee', 'Jane', 'Jessie', 'Kim', 'Chloe', 'Berry', 'Vinny', 
              'Dan', 'Bobby', 'Logan', 'Vin', 'Willy', 'Gin', 'Nicole', 'Karen', 'Lily', 'Eddie', 'James', 'Mandy', 'Donald', 'Peewee', 'Jeremy', 'Gray',
              'Bear', 'Jones', 'Nash', 'Candy', 'Louis', 'Tammy', 'Tim', 'Kyle', 'Badger', 'Wild', 'Jr', 'Raptor', 'Hawk', 'Edward', 'Bill', 'William']

APP_NAMES = ['Danger', 'Crap', 'Giant', 'Zoo', 'Beer', 'Puma', 'Tiger', 'Thunder', 'Barrel', 'Tanks', 'Flight', 'Stopper', 'Hunter', 'Jumper', 'Kick',
             'Zoom', 'Jam', 'Wow', 'Gunner', 'Shoot', 'Hat', 'Wall', 'Plus', 'Night', 'Tropic', 'Lightning', 'Exception', 'Ram', 'Drop', 'Juicy',
             'Catch', 'Battle', 'Combat', 'Fleet', 'Rock', 'Stone', 'Swim', 'Attack', 'Home', 'Base', 'Bunker', 'Car', 'Race', 'Rack', 'Stack']

REPO_NAMES = USER_NAMES + APP_NAMES

def get_any(ls):
    x = r.randint(0,len(ls)-1)
    return ls[x]

def get_any_many(ls, min_times, max_times):
    times = r.randint(min_times, max_times)
    xs = []
    for n in range(0,times):
        xs.append( get_any(ls) )
    return xs

def gen_random_repo_corpus(size=10000, config=DEFAULT_DB_CONFIG):
    app_builder_db = get_db(config=config)
    repo_col   = app_builder_db[COLL_REPOS]
    bcount_col = app_builder_db[COLL_BCOUNTS]
    for n in range(0,size):
        repo_recs, bcount_rec = gen_random_repo_records()
        repo_col.insert_many( repo_recs )
        bcount_col.insert_one( bcount_rec )

def gen_random_repo_records(size_range=[4,30]):
    size = r.randint(size_range[0], size_range[1])
    repo_recs = []
    user_name = ' '.join(get_any_many(USER_NAMES, 2, 3))
    repo_name = '-'.join(get_any_many(REPO_NAMES, 1, 4))
    for n in range(0,size):
        hash_id = "%032x" % getrandbits(128)
        app_recs = gen_random_app_records()
        store_loc = 0
        repo_rec = new_repo_record(user_name, repo_name, app_recs, store_loc, hash_id)
        repo_recs.insert(0, repo_rec)

    bcounts = 0
    for repo_rec in repo_recs:
        for app_rec in repo_rec[APPS]:
            bs = app_rec['builds']
            if len(bs) > 0:
                 if bs[0]['stat'] == STAT_BUILD_PASSED:
                      bcounts += 1
    bcount_rec = new_bcount_record(user_name, repo_name, bcounts)

    return repo_recs, bcount_rec

def gen_random_app_records(size_range=[1,1,1,1,2,2,3,4]):
    size = get_any(size_range)
    app_recs = []
    for n in range(0,size):
        app_name = '_'.join(get_any_many(APP_NAMES, 1, 4))
        build_recs = gen_random_build_records()
        app_rec = new_app_record(app_name, build_recs)
        app_recs.append( app_rec )
    return app_recs

DEFAULT_BUILD_RANGE = [STAT_BUILD_PASSED, STAT_BUILD_PASSED, STAT_BUILD_PASSED, STAT_BUILD_FAILED]

def gen_random_build_records(size_range=[1,6], build_range=DEFAULT_BUILD_RANGE):
    size = r.randint(size_range[0], size_range[1])
    build_recs = []
    for n in range(0,size):
       build_stat = get_any( build_range )
       snippet    = "Random snippet blah blah blah - %s" % r.randint(100000,9999999)
       build_rec  = new_build_record(build_stat, snippet)
       build_recs.insert(0, build_rec)
    return build_recs

