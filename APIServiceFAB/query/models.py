from __future__ import unicode_literals

from django.db import models

class GitUser(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return "GitUser<%s>" % self.name

class GitRepo(models.Model):
    user = models.ForeignKey(GitUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    def __str__(self):
        return "GitRepo<%s,%s>" % (self.user,self.name)

class StoreLoc(models.Model):
    name       = models.CharField(max_length=50)
    entry_ip   = models.CharField(max_length=50)
    store_type = models.CharField(max_length=20)
    def __str__(self):
        return "StoreLoc<%s,%s>" % (self.private_ip,self.store_type)

class GitCommit(models.Model):
    repo     = models.ForeignKey(GitRepo, on_delete=models.CASCADE)
    location = models.ForeignKey(StoreLoc, on_delete=models.CASCADE)
    hash_id  = models.CharField(max_length=50, primary_key=True)
    def __str__(self):
        return "GitCommit<%s,%s,%s>" % (self.repo,self.location,self.hash_id)

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


