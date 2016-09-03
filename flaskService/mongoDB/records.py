
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
DT_COMMITTED = 'dt_committed'	# Date and time this repo was committed (in GitHub)	**
PROJ_TYPE = 'ptype'		# Project type						**
STORE  = 'store'		# Storage location ID
APPS   = 'apps'			# Android application records
BUILDS = 'builds'               # Build records
DT_CREATED = 'dt_created'	# Date and time this record was created
DT_MODIFIED = 'dt_modified'     # Date and time this record was last modified


GRD_TYPE = 'GRD'
ANT_TYPE = 'ANT'
MAV_TYPE = 'MAV'
ECP_TYPE = 'ECP'
UNK_TYPE = 'UNK'

'''
REPO-REC :: { USER:<String>, REPO:<String>, HASH:<String>, DT_COMMITTED:<Int>, PROJ_TYPE:<String> , STORE:<Int>, APPS:<APP_DICT>, 
            , BUILDS:[<BUILD-REC>] , DT_CREATED:<Int>, DT_MODIFIED:<Int> }
'''
def new_repo_record(user_name, repo_name, dt_committed, proj_type, app_records, build_records, store_loc=0, hash_id="head"):
    time_now = get_epochtime_now()
    return { USER:user_name, REPO:repo_name, HASH:hash_id, DT_COMMITTED:dt_committed, PROJ_TYPE:proj_type, STORE:store_loc
           , APPS:app_records, BUILDS:build_records, DT_CREATED:time_now, DT_MODIFIED:time_now }


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
FIX_APPLIED = 'fix_applied'	# Fix heuristics applied			**
STAT    = 'stat'		# Build status
SNIPPET = 'snippet'		# Build outcome snippet

GRD_FIX_1 = 'GRD_FIX_1'
GRD_FIX_2 = 'GRD_FIX_2'

STAT_BUILD_TIMEDOUT = 'KO'
STAT_BUILD_SKIPPED  = 'SK'
STAT_BUILD_EXCEPT   = 'EX'
STAT_BUILD_FAILED   = 'FL'
STAT_BUILD_PASSED   = 'PS'
'''
BUILD-REC :: { BUILDER: <String>, FIX_APPLIED:[<String>], STAT:<Int>, SNIPPET:<String>, DT_CREATED:<Int> }
'''
def new_build_record(builder, fix_applied, build_stat, snippet, dt_created):
    return { BUILDER:builder, FIX_APPLIED:fix_applied, STAT:build_stat, SNIPPET:snippet, DT_CREATED:dt_created }

BUILDS  = 'builds'		# Total number of successful builds
FAILS   = 'fails'		# Total number of failed builds
SKIPS   = 'skips'		# Total number of skipped commits (no builds, e.g., no gradle files)
EXCEPTS = 'excepts'             # Total number of exception builds (exception occurred during build)
TIMEOUTS = 'timeouts'		# Total number of timed out builds
'''
BCOUNT-REC :: { USER:<String>, REPO:<String>, BUILDS:<Int>, FAILS:<INT>, SKIPS:<INT>, EXCEPTS:<INT>, TIMEOUTS:<INT> }
'''
def new_bcount_record(user_name, repo_name, builds, fails, skips, excepts, timeouts):
    return { USER:user_name, REPO:repo_name, BUILDS:builds, FAILS:fails, SKIPS:skips, EXCEPTS:excepts, TIMEOUTS:timeouts }

def bcount_field(stat):
    if stat == STAT_BUILD_PASSED:
        return BUILDS
    elif stat == STAT_BUILD_FAILED:
        return FAILS
    elif stat == STAT_BUILD_SKIPPED:
        return SKIPS
    elif stat == STAT_BUILD_EXCEPT:
        return EXCEPTS
    elif stat == STAT_BUILD_TIMEDOUT:
        return TIMEOUTS


