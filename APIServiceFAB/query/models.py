from __future__ import unicode_literals

from django.db import models

from django.db import transaction

LOCAL_BLOCK   = 'Local-Block'
LOCAL_ARCHIVE = 'Local-Archive'

REMOTE_BLOCK   = 'Remote-Block'
REMOTE_ARCHIVE = 'Remote-Archive'


class StoreLoc(models.Model):
    ip    = models.CharField(max_length=50)
    path  = models.CharField(max_length=50)
    stype = models.CharField(max_length=20)
    def __str__(self):
        return "StoreLoc<%s,%s,%s>" % (self.ip,self.path,self.stype)

class GitUser(models.Model):
    name = models.CharField(max_length=50)
    location = models.ForeignKey(StoreLoc, on_delete=models.CASCADE)
    def __str__(self):
        return "GitUser<%s,%s>" % (self.name,self.location)

class GitRepo(models.Model):
    user = models.ForeignKey(GitUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    def __str__(self):
        return "GitRepo<%s,%s>" % (self.user,self.name)

class GitCommit(models.Model):
    repo     = models.ForeignKey(GitRepo, on_delete=models.CASCADE)
    hash_id  = models.CharField(max_length=50, primary_key=True)
    def __str__(self):
        return "GitCommit<%s,%s>" % (self.repo,self.hash_id)

class GitApp(models.Model):
    commit   = models.ForeignKey(GitCommit, on_delete=models.CASCADE)
    app_name = models.CharField(max_length=50)
    def __str__(self):
        return "GitApp<%s,%s>" % (self.commit,self.app_name)

class GitBuild(models.Model):
    app      = models.ForeignKey(GitApp, on_delete=models.CASCADE)
    is_built = models.BooleanField(default=False) 
    snippet  = models.TextField()
    datetime = models.DateTimeField()
    def __str__(self):
        return "GitBuild<%s,%s,%s>" % (self.app, self.built, self.datetime)

def get_build_records(user_name, repo_name, hash_id=None, logging=None):
    gs = GitBuild.objects.filter( app__commit__repo__name=repo_name, app__commit__repo__user__name=user_name )
    if hash_id != None:
       gs = gs.filter( app__commit__hash_id=hash_id )
    gs = gs.order_by( 'datetime' )
    if logging != None:
       logging.info( "Retrieving build records: %s" % gs.query )

def get_latest_build_records(user_name, repo_name, hash_id=None, logging=None):
    gs = get_build_records(user_name, repo_name, hash_id, logging)
    if len(gs) > 0:
       return gs[0]
    else:
       return None

@transaction.atomic
def insert_record(user_name, repo_name, app_name, is_built, snippet, store_loc, hash_id='head', logging=None):
    user, user_created = GitUser.objects.get_or_create(name=user_name, location=store_loc)
    repo, repo_created = GitRepo.objects.get_or_create(user=user, name=repo_name)
    commit, commit_created = GitCommit.objects.get_or_create(repo=repo, hash_id=hash_id)
    app, app_created = GitApp.objects.get_or_create(commit=commit, app_name=app_name)
    datetime = models.DataTimeField(auto_now_add=True)
    git_build = GitBuild(app=app, is_built=is_built, snippet=snippet, datetime=datetime)
    git_build.save()
    if logging != None:
        log_str = "Inserted: User(%s) Repo(%s) Commit(%s) App(%s)" % (user_created, repo_created, commit_created, app_created)
        logging.info( log_str ) 
    return git_build

