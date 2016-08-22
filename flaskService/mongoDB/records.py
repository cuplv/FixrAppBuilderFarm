
from pymongo import MongoClient

from datetime import datetime
from pytz import reference

USER   = 'user'			# User name
REPO   = 'repo'			# Repository name
HASH   = 'hash'			# Commit Hash
STORE  = 'store'		# Storage location ID
APPS   = 'apps'			# Android application records
'''
REPO-REC :: { USER:<String>, REPO:<String>, HASH:<String>, STORE:<Int>, APPS:[<APP-REC>] }
'''
def new_repo_record(user_name, repo_name, app_records, store_loc=0, hash_id="head"):
    return { USER:user_name, REPO:repo_name, HASH:hash_id, STORE:store_loc, APPS:app_records }


APP    = 'app'			# Android application name
BUILDS = 'builds'		# Build records               
'''
APP-REC :: { APP:<String>, BUILDS:[<BUILD-REC>] }
'''
def new_app_record(app_name, build_records):
    return { APP:app_name, BUILDS:build_records }


STAT   = 'stat'			# Build status
SNIPPET = 'snippet'		# Build outcome snippet
DATETIME = 'datetime'		# Data and time of build (attempt)

STAT_BUILD_UNKNOWN = -1
STAT_BUILD_FAILED  = 0
STAT_BUILD_PASSED  = 1
'''
BUILD-REC :: { STAT:<Int>, SNIPPET:<String>, DATETIME:<String> }
'''
def get_pretty_datetime_now():
    now = datetime.now()
    localtime = reference.LocalTimezone()
    tz = localtime.tzname(now)
    return '%s %s' % (now.strftime("%T %D") , tz)

def new_build_record(build_stat, snippet):
    return { STAT:build_stat, SNIPPET:snippet, DATETIME:get_pretty_datetime_now() }

BCOUNT = 'bcount'		# Total number of successful builds
'''
BCOUNT-REC :: { USER:<String>, REPO:<String>, BCOUNT:<Int> }
'''
def new_bcount_record(user_name, repo_name, bcount):
    return { USER:user_name, REPO:repo_name, BCOUNT:bcount }



