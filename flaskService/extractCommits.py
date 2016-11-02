
import os
import json
import sys

from datetime import datetime

from gitUtils.gitdigger import getGitURLs


def get_epochtime_from_str(dt_str):
    dt = datetime.strptime(dt_str[:-1], '%Y-%m-%dT%H:%M:%S')
    return int(dt.strftime('%s'))

def extract_hash_and_date_info(input_csv, output_json, num_commits=3, wait=0.5):
   git_urls = []
   with open(input_csv, "r") as f:
       line = f.readline()
       while line != '':
          user_name,repo_name = line.replace("\n","").split(' ')
          git_url = "https://api.github.com/repos/%s/%s/commits?page=1&per_page=%s" % (user_name,repo_name,num_commits)
          git_urls.append( git_url )
          line = f.readline()

   print("Read %s repos" % len(git_urls))

   with open(output_json, "w") as o:

      def format_output_json(user_name, repo_name, hash_id, dt_committed):
         return { 'user':user_name, 'repo':repo_name, 'hash':hash_id, 'dt_committed':dt_committed }

      def write_func(resp):
         jsons = []
         for commit in resp['body']:
             # 2016-01-31T08:12:15Z
             raw_date = commit['commit']['committer']['date']
             dt_committed = get_epochtime_from_str( raw_date )
             # "https://api.github.com/repos/sllam/comingle/commits/f94528cdba7d7b1fefbba4d3cd8f5767eac50ef1"
             url_frags = commit['url'][29:].split('/')
             user = url_frags[0]
             repo = url_frags[1]
             hash_id = commit['sha']
             data = format_output_json(user, repo, hash_id, dt_committed)
             o.write( "%s\n" % json.dumps( data ) )
             o.flush()
             jsons.append( data )
         return jsons

      return getGitURLs(git_urls, wait=1, func=write_func)


if __name__ == "__main__":
   args = sys.argv
   if len(args) != 3:
       print "Usage: python %s <csv file: 'userName repoName'> <# latest commits>" % args[0]
       sys.exit(0)
   input_csv      = args[1]
   num_of_commits = args[2]
   output_json = input_csv.split(".")[0] + ".json"
   print "Extracting latest %s commits from GitHub repositoies in %s and writing to %s" % (num_of_commits, input_csv, output_json)

   resps, failed = extract_hash_and_date_info(input_csv, output_json, num_commits=num_of_commits, wait=0.5)

   print "Done!! Written output to %s" % output_json
   print "Extracted from %s repos from GitHub. Failed in %s" % (len(resps), len(failed))


