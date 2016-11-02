
import os
import sys
import time
import traceback
import optparse
import json
import logging
import StringIO
import pprint

import urllib2
import base64
import re

from Queue import Queue
from threading import Thread



URL_GIT_API = "https://api.github.com"
URL_GIT_REPOS_API = URL_GIT_API + "/repos" 

URL_GIT_HTML = "https://github.com"

GIT_NAME = "sllam"
GIT_PW   = "beccaTmsigma89515515515$"

GIT_LOGGER = logging.getLogger('gitdigger')
GIT_LOGGER.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
GIT_LOGGER.addHandler(ch)


def getJsonURL(api_url, auth_creds=(GIT_NAME,GIT_PW)):
   try:
      request = urllib2.Request(api_url)
      if auth_creds is not None:
         username,password = auth_creds
         base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
         request.add_header("Authorization", "Basic %s" % base64string)
      resp = urllib2.urlopen(request)
      http_info = resp.info()
      raw_data = resp # .decode(http_info.get_content_charset())
      project_info = json.load(raw_data)
      GIT_LOGGER.info("Data successfully retrieved from %s with %s's creds" % (api_url,auth_creds[0]) )
      print json.dumps(project_info, indent=4, sort_keys=True)
      return {'headers': http_info.items(), 'body': project_info}
   except:
      exc_type, exc_value, exc_traceback = sys.exc_info()
      lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
      GIT_LOGGER.warning("Error occurred with querying %s!\n%s" % (api_url,'\n'.join(lines)) )
      return None

def getJsonURLs(api_urls, wait=1):
   resps = []
   count = 0
   GIT_LOGGER.info("Starting fetch sequence of %s URLs" % len(api_urls))
   for api_url in api_urls:
     resp = getJsonURL(api_url)
     if resp != None:
        count += 1
        resps += [resp]
     GIT_LOGGER.debug("Sleeping...")
     time.sleep(wait)
     GIT_LOGGER.debug("Wake...")
   GIT_LOGGER.info("Done! %s URLs fetched" % count)
   return resps


def getJsonURLLoop(queue, wait=1):
   while True:
      req_urls,fut = queue.get(block=True)
      resps = []
      for req_url in req_urls:
         resps += [getJsonURL(req_url, auth_creds=(GIT_NAME,GIT_PW) )]
         GIT_LOGGER.debug("Sleeping...")
         time.sleep(wait)
         GIT_LOGGER.debug("Wake...")
      fut.put(resps)

def reqJsonURLs(queue, req_urls):
   fut = Queue()
   queue.put( (req_urls,fut) )
   GIT_LOGGER.debug("Waiting on URL fetch daemon...")  
   resps = fut.get(block=True)
   GIT_LOGGER.debug("Received response from URL fetch daemon!")
   return resps
 
def reqJsonURL(queue, req_url):
   return reqJsonURLs(queue, [req_url])[0]

def getPaginatedURL(queue, api_url, start_page=1, per_page=30, num_of_pages=-1):
   if num_of_pages == -1:
      end_page = 100000
   else:
      end_page = start_page + num_of_pages
   end = False
   curr_page = start_page
   resps = []
   while curr_page < end_page and not end :
      resp = reqJsonURL(queue, "%s?page=%s&per_page=%s" % (api_url,curr_page,per_page) )
      resps += [resp]
      if len(resp['body']) < per_page - 1:
         end = True
      curr_page += 1
   return resps,end


def getGitURLs(git_urls, wait=1, func=lambda x: x):
   queue = Queue()
   t = Thread(target=getJsonURLLoop, args=(queue, wait))
   t.daemon = True
   t.start()
   resps = []
   failed = []
   for git_url in git_urls:
      resp = reqJsonURL(queue, git_url)
      if resp != None:
         resps.append( func(resp) )
      else:
         failed.append( git_url ) 
   return resps, failed


