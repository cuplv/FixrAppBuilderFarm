
import os
import shutil
import time

from os.path import isfile, isdir, join

def getFilesInPath(path):
    return [join(path, f) for f in os.listdir(path) if isfile(join(path, f))]

def getDirsInPath(path):
    return [join(path, f) for f in os.listdir(path) if isdir(join(path, f))]

def createBuildMap(buildPath):
    buildMap = {}
    for userPath in getDirsInPath(buildPath):
        userName = os.path.basename(userPath)
        userMap = {}
        buildMap[userName] = userMap
        for repoPath in getDirsInPath(userPath):
            repoName = os.path.basename(repoPath)
            repoMap = {}
            userMap[repoName] = repoMap
            for hashPath in getDirsInPath(repoPath):
                hashName = os.path.basename(hashPath)
                repoMap[hashName] = hashPath
    return buildMap

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def migrateBuildRepos(refRepos, srcRepos, destRepos, outputPath):
    refBMap = createBuildMap(refRepos)
    srcBMap = createBuildMap(srcRepos)

    missing_users = []
    missing_repos = []
    missing_hash = []
    for user in refBMap:
       if user not in srcBMap:
          missing_users.append( user )
          print "User %s is missing!" % user
          refUMap = refBMap[user]
          srcUMap = {}
       else:
          refUMap = refBMap[user]
          srcUMap = srcBMap[user]
       for repo in refUMap:
           if repo not in srcUMap:
              missing_repos.append( "%s/%s" % (user,repo) )
              print "Repo %s/%s is missing!" % (user,repo)
           else:
              refRMap = refUMap[repo]
              srcRMap = srcUMap[repo]
              for hashId in refRMap:
                  if hashId not in srcRMap:
                      missing_hash.append( "%s/%s/%s" % (user,repo,hashId) )
                      print "Hash %s/%s/%s is missing!" % (user,repo,hashId)
                  else:
                      srcPath  = srcRMap[hashId]
                      destPath = destRepos + remove_prefix(srcPath, srcRepos)
                      shutil.copytree(srcPath, destPath)
    
    print "%s users missing" % len(missing_users)
    print "%s repos missing" % len(missing_repos)
    print "%s hashs missing" % len(missing_hash)

    with open(outputPath + '/missing_users', 'w') as f:
        f.write( '\n'.join( missing_users ) )    

    with open(outputPath + '/missing_repos', 'w') as f:
        f.write( '\n'.join( missing_repos ) )    

    with open(outputPath + '/missing_hash', 'w') as f:
        f.write( '\n'.join( missing_hash ) )

    print "Done!"
