from __future__ import print_function
from flask import session
import base64
import json
import requests
import sys

# Workaround to support both python 2 & 3
try:
    import urllib.request, urllib.error
    import urllib.parse as urllibparse
except ImportError:
    import urllib as urllibparse


SPOTIFY_API_BASE_URL = 'https://api.spotify.com'
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# ----------------- 1. USER AUTHORIZATION ----------------

# spotify endpoints
SPOTIFY_AUTH_BASE_URL = "https://accounts.spotify.com/{}"
SPOTIFY_AUTH_URL = SPOTIFY_AUTH_BASE_URL.format('authorize')
SPOTIFY_TOKEN_URL = SPOTIFY_AUTH_BASE_URL.format('api/token')

# client keys
# CLIENT = json.load(open('conf.json', 'r+'))
CLIENT_ID = 'fc1d06d724f1471c8f92aaf37e8932f5'
CLIENT_SECRET = '5916cd1c390d4c89a438b2088642f9bd'

# server side parameter
# * fell free to change it if you want to, but make sure to change in
# your spotify dev account as well *
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8081
REDIRECT_URI = "{}:{}/callback/".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private user-read-recently-played user-top-read"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


# token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown
TOKEN_DATA = []
REFRESH_TOKEN = ''
# https://developer.spotify.com/web-api/authorization-guide/
auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}


URL_ARGS = "&".join(["{}={}".format(key, urllibparse.quote(val))
                         for key, val in list(auth_query_parameters.items())])
AUTH_URL = "{}/?{}".format(SPOTIFY_AUTH_URL, URL_ARGS)


def authorize(auth_token):
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }


    base64encoded = base64.b64encode(("{}:{}".format(CLIENT_ID, CLIENT_SECRET)).encode())
    headers = {"Authorization": "Basic {}".format(base64encoded.decode())}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # tokens are returned to the app
    response_data = post_request.json()

    # For saving the token in file
    token = json.dumps(response_data, indent=4)
    file = '{}.json'.format('token')
    with open(file, 'w+') as f:
        f.write(token)

    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    session['refresh_token'] = refresh_token
    current_datetime = datetime.datetime.now()
    expiry_datetime = current_datetime + datetime.timedelta(0, 3600)
    session['expiry_datetime'] = expiry_datetime

    # use the access token to access Spotify API
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    return auth_header


def handleToken(response):
    auth_header = {"Authorization": "Bearer {}".format(response["access_token"])}
    session['refresh_token'] = response["refresh_token"]
    current_datetime = datetime.datetime.now()
    expiry_datetime = current_datetime + datetime.timedelta(0, 3600)
    session['expiry_datetime'] = expiry_datetime
    session['auth_header'] = auth_header
    print('Refreshed Token')
    return auth_header


def refreshAuth():
    body = {
        "grant_type": "refresh_token",
        "refresh_token": session['refresh_token']
    }

    post_refresh = requests.post(SPOTIFY_TOKEN_URL, data=body, headers=HEADER)
    p_back = json.dumps(post_refresh.text)

    return handleToken(p_back)


# spotify endpoints
USER_PROFILE_ENDPOINT = "{}/{}".format(SPOTIFY_API_URL, 'me')
USER_PLAYLISTS_ENDPOINT = "{}/{}".format(USER_PROFILE_ENDPOINT, 'playlists')
USER_TOP_ARTISTS_AND_TRACKS_ENDPOINT = "{}/{}".format(
    USER_PROFILE_ENDPOINT, 'top')  # /<type>
USER_RECENTLY_PLAYED_ENDPOINT = "{}/{}/{}".format(USER_PROFILE_ENDPOINT,
                                                  'player', 'recently-played')
BROWSE_FEATURED_PLAYLISTS = "{}/{}/{}".format(SPOTIFY_API_URL, 'browse',
                                              'featured-playlists')

PLAYLIST_DETAILS = 'https://api.spotify.com/v1/playlists/'


# https://developer.spotify.com/web-api/get-users-profile/
def get_users_profile(auth_header):
    url = USER_PROFILE_ENDPOINT
    resp = requests.get(url, headers=auth_header)
    return resp.json()


# https://developer.spotify.com/console/get-playlist-tracks/
def get_tracks(playlist_id, auth_header):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    resp = requests.get(url, headers=auth_header)
    return resp.json()