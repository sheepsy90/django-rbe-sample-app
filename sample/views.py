import uuid

import django.contrib.auth as djauth

import requests
import requests.auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect, HttpResponse

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.urls import reverse

from sample.models import Profile


@login_required()
def index(request):
    rc = RequestContext(request)
    print request.user
    rc['somelist'] = [1, 2, 3, 4, 5]
    rc['user'] = request.user
    return render_to_response('index.html', rc)

def landing(request):
    print request.user
    if hasattr(request, 'user') and request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    rc = RequestContext(request)
    return render_to_response('landing.html', rc)

@login_required
def logout(request):
    rc = RequestContext(request)
    djauth.logout(request)
    return HttpResponseRedirect(reverse('landing'), rc)


def auth_callback(request):
    """ Handles the auth callback from the RBE Network """
    # This should make some steps:
    # Eg. checking the state, and verifying that it was issued by yourself
    # Get an API token to query the user
    # Login the user if the user is not logged in or create a user
    print request.GET

    error = request.GET.get('error')
    state = request.GET.get('state')
    code = request.GET.get('code')

    if not is_valid_state(state):
        # Uh-oh, this request wasn't started by us!
        return HttpResponse(status=403)

    # We'll change this next line in just a moment
    try:
        access_token = get_token(code)
        print access_token
    except:
        return HttpResponse("Could not retrieve token")

    user_properties = get_username(access_token)
    uid = user_properties.get('uid')
    username = user_properties.get('username')
    email = user_properties.get('email')

    made_up_password = str(uuid.uuid4())

    try:
        p = Profile.objects.get(uid=uid)
    except Profile.DoesNotExist:
        u = User.objects.create_user(username=username, email=email, password=made_up_password)
        p = Profile(uid=uid, user=u, password=made_up_password)
        p.save()

    user = djauth.authenticate(username=p.user.username, password=p.password)
    djauth.login(request, user)

    return HttpResponseRedirect(reverse('index'))


def authorize_at_core(request):
    return HttpResponseRedirect(make_authorization_url())


def make_authorization_url():
    # Generate a random string for the state parameter
    # Save it for use later to prevent xsrf attacks
    from uuid import uuid4
    state = str(uuid4())
    save_created_state(state)
    params = {"client_id": settings.CLIENT_ID,
              "response_type": "code",
              "state": state,
              "redirect_uri": settings.REDIRECT_URI,
              "duration": "temporary",
              "scope": "identity openid profile email location"}
    import urllib
    url = "{}/authorize?".format(settings.SITE_URL) + urllib.urlencode(params)
    return url

# Left as an exercise to the reader.
# You may want to store valid states in a database or memcache,
# or perhaps cryptographically sign them and verify upon retrieval.
def save_created_state(state):
    pass

def is_valid_state(state):
    return True


def get_username(access_token):
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get("{}/core/api/identity?token={}".format(settings.SITE_URL, access_token), headers=headers)
    print response.status_code, response.content
    return response.json()


def get_token(code):
    client_auth = requests.auth.HTTPBasicAuth(settings.CLIENT_ID, settings.CLIENT_SECRET)
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": settings.REDIRECT_URI}
    print post_data
    print "{}/token?".format(settings.SITE_URL)
    response = requests.post("{}/token".format(settings.SITE_URL),
                             auth=client_auth,
                             data=post_data)

    print response.content, response.status_code

    token_json = response.json()
    return token_json["access_token"]
