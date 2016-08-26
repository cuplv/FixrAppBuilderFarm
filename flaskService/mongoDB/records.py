
from pymongo import MongoClient

from datetime import datetime
from pytz import reference

# Basic Datetime libraries

def get_pretty_datetime_now():
    now = datetime.now()
    localtime = reference.LocalTimezone()
    tz = localtime.tzname(now)
    return '%s %s' % (now.strftime("%T %D") , tz)

def get_epochtime_now():
    now = datetime.now()
    return int(now.strftime("%s"))

def get_datetime_from_epochtime(epochtime):
    return datetime.fromtimestamp(epochtime)

def pretty_datetime(datetime):
    localtime = reference.LocalTimezone()
    tz = localtime.tzname(datetime)
    return '%s %s' % (datetime.strftime("%T %D") , tz)

def pretty_epochtime(epochtime):
    return pretty_datetime( get_datetime_from_epochtime(epochtime) )

# Record formats

USER   = 'user'			# User name
REPO   = 'repo'			# Repository name
HASH   = 'hash'			# Commit Hash
STORE  = 'store'		# Storage location ID
APPS   = 'apps'			# Android application records
BUILDS = 'builds'               # Build records
DT_CREATED = 'dt_created'	# Date and time this record was created
DT_MODIFIED = 'dt_modified'     # Date and time this record was last modified
'''
REPO-REC :: { USER:<String>, REPO:<String>, HASH:<String>, STORE:<Int>, APPS:<APP_DICT>, BUILDS:[<BUILD-REC>] , DT_CREATED:<Int>, DT_MODIFIED:<Int> }
'''
def new_repo_record(user_name, repo_name, app_records, build_records, store_loc=0, hash_id="head"):
    time_now = get_epochtime_now()
    return { USER:user_name, REPO:repo_name, HASH:hash_id, STORE:store_loc, APPS:app_records, BUILDS:build_records
           , DT_CREATED:time_now, DT_MODIFIED:time_now }


SRC   = 'src'		# Paths to the .java files (each corresponds to a directory where .java files a located at)
CLASS = 'cls'		# Paths to the .class files (each corresponds to a directory where .class files a located at)
JAR   = 'jar'		# Paths to classes.jar files (each corresponds to a specific classes.jar file)
APK   = 'apk'		# Paths to the apks. (each corresponds to a specific .apk file)
OTHERS = '_others'      # This key corresponds to app records that are not classified as belonging to an app.
'''
APP-DICT :: { <APP_NAME_1>:<APP-REC>, ..., <APP_NAME_n>:<APP-REC>, '_others':<APP-REC> }

APP-REC :: { SRC:[<String>], CLASS:[<String>], JAR:[<String>], APK:[<String>] }
'''
def new_app_record(src_path=[], class_path=[], jar_path=[], apk_path=[]):
    return { SRC:src_path, CLASS:class_path, JAR:jar_path, APK:apk_path }


BUILDER = 'builder'		# Name of builder who attempted this         
STAT    = 'stat'		# Build status
SNIPPET = 'snippet'		# Build outcome snippet

STAT_BUILD_UNKNOWN = -1
STAT_BUILD_FAILED  = 0
STAT_BUILD_PASSED  = 1
'''
BUILD-REC :: { BUILDER: <String>, STAT:<Int>, SNIPPET:<String>, DT_CREATED:<Int> }
'''
def new_build_record(builder, build_stat, snippet):
    return { BUILDER:builder, STAT:build_stat, SNIPPET:snippet, DT_CREATED:get_epochtime_now() }

BCOUNT = 'bcount'		# Total number of successful builds
'''
BCOUNT-REC :: { USER:<String>, REPO:<String>, BCOUNT:<Int> }
'''
def new_bcount_record(user_name, repo_name, bcount):
    return { USER:user_name, REPO:repo_name, BCOUNT:bcount }



