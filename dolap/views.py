from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

from dropbox import client, rest, session
from oauth import oauth

from dolap.models import User, File, Shelf

APP_KEY = '452mpmxv6d354xd'
APP_SECRET = 'ihol6nu966f9ts5'
ACCESS_TYPE = 'app_folder'

def require_in_session(key, redirect):
    def df(f):
        def ddf(request, *args, **kwargs):
            if request.session.has_key(key):
                return f(request, *args, **kwargs)
            return HttpResponseRedirect(redirect)
        return ddf

    return df

def intro(request):
    if request.session.has_key('dropbox_client') or \
        request.session.has_key('oauth_token'):
        return home(request)
    return render_to_response('intro.html', {'page': 'home'})

def logout(request):
    request.session.clear()
    return intro(request)

def login(request):
    cl = request.session.get('dropbox_client', False)
    sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
    if not cl:
        # user haven't logged in yet
        if request.session.has_key('oauth_token'):
            # user have just allowed dropbox, create a session
            try:
                access_token = sess.obtain_access_token(request.session['oauth_token'])
                cl = client.DropboxClient(sess)
            except client.ErrorResponse:
                # delete oauth_token and try again from beginning
                del request.session['oauth_token']
                return login(request)
            else:
                request.session['dropbox_client'] = cl
                return HttpResponseRedirect('/app/home')
        else:
            request_token = sess.obtain_request_token()
            url = sess.build_authorize_url(request_token)

            # request.session['oauth_token'] = request_token.to_string()
            request.session['oauth_token'] = request_token
            return HttpResponseRedirect(url)

    return HttpResponseRedirect('/app/home')

@require_in_session('dropbox_client', '/app/login')
def home(request):
    """Homepage of the user."""
    cl = request.session['dropbox_client']
    user_info = cl.account_info()
    # linked account: {'referral_link': 'https://www.dropbox.com/referrals/NTY2MzYzODEzOQ',
    # 'display_name': 'dolap app', 'uid': 66363813, 'country': 'TR',
    # 'quota_info': {'shared': 3180657, 'quota': 2147483648, 'normal': 1421746},
    # 'email': 'dolapapp@gmail.com'}
    user = User.objects.get_or_create(uid=user_info['uid'])

    return render_to_response('home.html', cl.account_info())