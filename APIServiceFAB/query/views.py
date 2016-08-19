from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q

from models import GitUser, GitRepo, StoreLoc, GitCommit, GitApp, GitBuild

# Create your views here.

from django.http import HttpResponse


def index(request):

    print request.GET.get('q', '')

    # qs = GitBuild.objects.filter( app__commit__repo__name='foo', app__commit__repo__user__name='bar' )

    qs1 = GitBuild.objects.filter(reduce(lambda x, y: x | y, [Q(app__commit__repo__name__contains=word) for word in ['foo','bar']]))
    qs2 = qs1.filter( reduce(lambda x, y: x | y, [Q(app__commit__repo__user__name__contains=word) for word in ['woo','par']]) )

    print qs2.query

    return JsonResponse({ 'foo': len(qs1) })
    # return HttpResponse("Hello, world. You're at the polls index.")

def format_inputs(gets):

    args = {}

    def extend(get_param, arg_param=None):
        val = gets.get(get_param, None)
        if val is not None:
            arg_param = arg_param if arg_param is not None else get_param
            if arg_param not in args:
                args[arg_param] = []
            args[arg_param] += [val]

    def set_arg(get_param, f=lambda x: x):
        val = gets.get(get_param, None)
        if val != None:
            args[get_param] = f(val)

    def set_boolarg(get_param):
        val = gets.get(get_param, None)
        if val is not None:
            if val in ['0','false','False']:
                args[get_param] = False
            else:   
                args[get_param] = True

    extend('user','users')
    extend('users','users')
    extend('repo','repos')
    extend('repos','repos')
    extend('hash_id','hash_ids')
    extend('hash_ids','hash_ids')
    set_arg('offset', int)
    set_arg('limit', int)
    set_boolarg('ordered')
    set_boolarg('buildable')

    return args

def query_build_records(request):
    
    args = format_inputs(request.GET)

    qs = GitApp.objects
    if 'buildable' in args:
        qs = qs.filter( gitbuild__is_built__contains=args['buildable'] )
    if 'repos' in args:
        qs = qs.filter( reduce(lambda x, y: x | y, [Q(commit__repo__name__contains=user) for user in args['repos']]) )
    if 'users' in args:
        qs = qs.filter( reduce(lambda x, y: x | y, [Q(commit__repo__user__name__contains=user) for user in args['users']]) )
    if 'hash_ids' in args:
        qs = qs.filter( reduce(lambda x, y: x | y, [Q(commit__hash_id__contains=user) for user in args['hash_ids']]) )
    if 'offset' in args and 'limit' in args:
        qs = qs.all()[args['offset']:(args['offset']+args['limit'])]
    elif 'offset' not in args and 'limit' in args:
        qs = qs.all()[:args['limit']]
    elif 'offset' in args and 'limit' not in args:
        qs = qs.all()[args['offset']:]

    print qs.query

    return JsonResponse({ 'foo': len(qs) })
    
