from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from dropbox import client, rest, session

from dolap.models import User, File, Shelf
from gravatar import create_gravatar_link

import datetime
import json

APP_KEY = '452mpmxv6d354xd'
APP_SECRET = 'ihol6nu966f9ts5'
ACCESS_TYPE = 'app_folder'

months = {['Jan', 'Feb', 'Mar', 'Apr', 'May',
    'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][i-1]:i for i in range(1, 13)}


# these fields will be read from Dropbox API's file dict and written to db
file_required_fields = ['path', 'size', 'modified', 'revision',
    'mime_type', 'owner', 'added', 'share_link']

def datetime_to_json(datetime):
    return datetime.strftime("%d-%m-%Y %H:%M:%S")

# def json_to_datetime(json):
#     return json.strptime("%d %m %Y %H:%M:%S")

def filelist_to_json(files):
    json_list = []
    for f in files:
        d = {k:files[k] for k in file_required_fields}
        d['added'] = datetime_to_json(d['added'])
        d['updated'] = datetime_to_json(d['updated'])
        json_list.append(d)
    return json_list

def last_updated_files(count=10):
    return filelist_to_json(File.objects.order_by('modified')[:count])

def last_added_files(count=10):
    return filelist_to_json(File.objects.order_by('added')[:count])

def json_last_added_files(request):
    return HttpResponse(last_added_files(count=int(request.GET.get('count', 10))))

def json_last_updated_files(request):
    return HttpResponse(last_updated_files(count=int(request.GET.get('count', 10))))

def collect_files(path, client, result):
    """Recursively collect files in path and it's subfolders using an Dropbox client"""
    files = client.metadata(path)['contents']
    print files
    for f in files:
        if f['is_dir']:
            collect_files(f['path'], client, result)
        else:
            result.append(f)

    return result

def require_in_session(key, redirect):
    def df(f):
        def ddf(request, *args, **kwargs):
            if request.session.has_key(key):
                return f(request, *args, **kwargs)
            return HttpResponseRedirect(redirect)
        return ddf

    return df

def require_in_session_json(key):
    def df(f):
        def ddf(request, *args, **kwargs):
            if request.session.has_key(key):
                return f(request, *args, **kwargs)
            return HttpResponse(json.dumps({'status': 'error',
                                            'reason': 'you sould login to call this service.'}))
        return ddf

    return df



def intro(request):
    if request.session.has_key('dropbox_client') or \
        request.session.has_key('oauth_token'):
        return HttpResponseRedirect('/app/home/')
        # return user_home(request)
    return render_to_response('intro.html', {})

def logout(request):
    request.session.clear()
    return HttpResponseRedirect('/app/')
    # return intro(request)

@require_in_session_json('user')
def json_edit_file(request):
    # TODO: may need to change GET to POST for security reasons
    path = request.GET['path']
    try:
        f = File.objects.get(path=path, owner=request.session['user'])
    except File.DoesNotExist:
        return HttpResponse(json.dumps({'status': 'error', 'reason': 'file does not exist'}))

    f.description = request.GET['description']
    f.shelves.clear()
    for s in request.GET['shelves'].split(', '):
        ss = s.strip()
        if ss:
            f.shelves.add(Shelf.objects.get(name=ss))
    f.save()

    return HttpResponse(json.dumps({'status': 'ok'}), 'application/json')

def json_login(request):
    cl = request.session.get('dropbox_client', False)
    sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
    mime_type = 'application/json'
    print request.session.keys()
    if not cl:
        # user haven't logged in yet
        if request.session.has_key('oauth_token'):
            # user has just allowed dropbox, create a session
            print "oauth token var"
            try:
                print request.session['oauth_token']
                access_token = sess.obtain_access_token(request.session['oauth_token'])
                cl = client.DropboxClient(sess)
            except client.ErrorResponse as e:
                print e
                # delete oauth_token and try again from beginning
                print "oauth token hata"
                del request.session['oauth_token']
                return json_login(request)
            else:
                request.session['dropbox_client'] = cl
                user_info = cl.account_info()
                user_info['gravatar_url'] = create_gravatar_link(user_info['email'])
                request.session['user_info'] = user_info
                return HttpResponse(json.dumps({'response': 'ok'}), mime_type)
                # return HttpResponseRedirect('/app/home')
        else:
            request_token = sess.obtain_request_token()
            url = sess.build_authorize_url(request_token)

            # request.session['oauth_token'] = request_token.to_string()
            request.session['oauth_token'] = request_token
            return HttpResponse(json.dumps({'response': 'fail', 'url': url}), mime_type)
            # return HttpResponseRedirect(url)

    # return HttpReponse(json.dumps({'response': 'ok'}), mime_type)
    # return HttpResponseRedirect('/app/home')

@require_in_session('dropbox_client', '/app/')
def home(request):
    """/app/home/"""
    cl = request.session['dropbox_client']
    user_info = cl.account_info()

    user, is_new = User.objects.get_or_create(uid=user_info['uid'])
    if is_new:
        user.display_name = user_info['display_name']
        user.email = user_info['email']
        user.save()
    request.session['user'] = user

    d = {'last_updates': File.objects.order_by('modified')[:10],
         'last_added': File.objects.order_by('added')[:10],
         'shelves': Shelf.objects.filter(parent=None),
         'page': 'home',
         'is_new': is_new}

    return render_to_response('home.html', d, context_instance=RequestContext(request))

@require_in_session_json('user')
def json_file_details(request, file=None):
    try:
        f = File.objects.get(path=file)
    except File.DoesNotExist:
        return HttpResponse(json.dumps({'result': 'fail', 'reason': 'file does not exist'}))

    d = {'file': f, 'owner': False}
    if request.session['user'] == f.owner:
        d['owner'] = True

    return HttpResponse(json.dumps(d), mime_type='application/json')

@require_in_session('user', '/app/')
def file_details(request, file_owner=None, path=None):
    try:
        user = User.objects.get(uid=file_owner)
    except User.DoesNotExist:
        pass
    else:
        try:
            f = File.objects.get(path=path, owner=user)
        except File.DoesNotExist:
            pass
        else:
            d = {'file': f,
                 'owner': request.session['user'].uid == user.uid,
                 'shelves': f.shelves.all(),
                 'allshelves': Shelf.objects.all()}

            return render_to_response('details.html', d, context_instance=RequestContext(request))

@require_in_session_json('user')
def json_file_list(request):
    #cl = request.session['dropbox_client']
    #user_info = cl.account_info()

    #user, is_new = User.objects.get_or_create(uid=user_info['uid'])
    #request.session['user'] = user
    #request.session['account'] = user_info

    #if is_new:
        #user.email = user_info['email']
        #user.display_name = user_info['display_name']
        #user.save()
        #json_update_files(request)

    user = request.session['user']

    json_list = [{'path': f.path, 'size': f.size,
                  'modified': datetime_to_json(f.modified), 'owner': user.uid} \
        for f in user.file_set.all()]

    print json_list
    return HttpResponse(json.dumps(json_list), 'application/json')

@require_in_session('dropbox_client', '/app/')
def json_update_files(request):
    user = request.session['user']
    # for f in File.objects.filter(owner=user):
    #     f.delete()

    cl = request.session['dropbox_client']
    files = collect_files('/', cl, [])
    for f in files:
        # update files instead of creating new
        try:
            dbf = File.objects.get(path=f['path'], owner=user)
        except File.DoesNotExist:
            print "new file"
            f['owner'] = user
            f['added'] = datetime.datetime.now()
            tokens = f['modified'].split()
            modified_date = datetime.datetime.strptime(
                "%s %02d %s %s" % (tokens[1], months[tokens[2]], tokens[3], tokens[4]),
                "%d %m %Y %H:%M:%S")
            f['modified'] = modified_date
            f['share_link'] = cl.share(f['path'])['url']
            print "share_link:", f['share_link']
            fm = File(**{field : f[field] for field in file_required_fields})
            fm.added = datetime.datetime.now()
            fm.save()
            print f
        else:
            print "update file"
            tokens = f['modified'].split()
            modified_date = datetime.datetime.strptime(
                "%s %02d %s %s" % (tokens[1], months[tokens[2]], tokens[3], tokens[4]),
                "%d %m %Y %H:%M:%S")
            dbf.modified = modified_date
            dbf.share_link = cl.share(f['path'])['url']
            dbf.size = f['size']
            dbf.revision = f['revision']


    json_list = [{'path': f.path, 'size': f.size, 'owner': f.owner.uid,
        'modified': datetime_to_json(f.modified)} \
        for f in user.file_set.all()]

    return HttpResponse(json.dumps(json_list), 'application/json')

@require_in_session_json('user')
def json_follow_user(request, uid):
    user_info = request.session.get('user_info', False)
    try:
        user = User.objects.get(uid=user_info['uid'])
        user.following.add(User.objects.get(uid=int(uid)))
    except User.DoesNotExist as e:
        print "doesnotexist"
        return HttpResponse(json.dumps({'response': 'error'}))
    return HttpResponse(json.dumps({'response': 'ok'}))

@require_in_session_json('user')
def json_unfollow_user(request, uid):
    user_info = request.session.get('user_info', False)
    try:
        user = User.objects.get(uid=user_info['uid'])
        user.following.remove(User.objects.get(uid=int(uid)))
    except User.DoesNotExist as e:
        print "doesnotexist"
        return HttpResponse(json.dumps({'response': 'error'}))
    return HttpResponse(json.dumps({'response': 'ok'}))

@require_in_session('user', '/app/')
def shelf(request, shelf=None):
    try:
        s = Shelf.objects.get(name=shelf)
    except Shelf.DoesNotExist:
        pass
    else:
        files = s.file_set.all()
        parents = []
        parent = s.parent
        while parent:
            parents = [parent] + parents
            parent = parent.parent

        subshelves = s.shelf_set.all()
        d = {'files': files, 'subshelves': subshelves, 'parents': parents,
             'shelf': shelf, 'account': request.session.get('user_info', False)}
        return render_to_response('shelf.html', d, context_instance=RequestContext(request))

@require_in_session('user', '/app/')
def profile(request, uid):
    profile = User.objects.get(uid=uid)
    user_info = request.session.get('user_info', False)
    d = {'profile': profile,
         'account': user_info}
    if user_info:
        d['loggedacc'] = User.objects.get(uid=user_info['uid'])
    return render_to_response('profile.html', d, context_instance=RequestContext(request))

@require_in_session('user', '/app/')
def files(request):
    # we have a special case here
    # require_in_session doesn't work
    #if not request.session.has_key('dropbox_client'):
        #request.session.clear()
        #return HttpResponseRedirect("/app/")

    # if not user_info:
    #     user_info = cl.account_info()
    #     request.session['user_info'] = user_info
    # linked account: {'referral_link': 'https://www.dropbox.com/referrals/NTY2MzYzODEzOQ',
    # 'display_name': 'dolap app', 'uid': 66363813, 'country': 'TR',
    # 'quota_info': {'shared': 3180657, 'quota': 2147483648, 'normal': 1421746},
    # 'email': 'dolapapp@gmail.com'}

    d = {'page': 'files'}
    return render_to_response('user_home.html', d, context_instance=RequestContext(request))
