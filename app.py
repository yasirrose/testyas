'''
    This code was based on these repositories,
    so special thanks to:
        https://github.com/datademofun/spotify-flask
        https://github.com/drshrey/spotify-flask-auth-example

'''

from flask import Flask, request, redirect, g, render_template, session
from spotify_requests import spotify
import json

import sqlite3
from os import path,getcwd
import re
import os
import sys

app = Flask(__name__)
app.secret_key = 'some key for session'

def db_connection():
    database = path.join(getcwd(), 'pythonsqlite.db')
    # if not path.exists(database):
    #     print('Database file does not exists please check')
    #     exit()
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection

# ----------------------- AUTH API PROCEDURE -------------------------

@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)


@app.route("/callback/")
def callback():

    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header

    return profile()

def valid_token(resp):
    return resp is not None and not 'error' in resp

# -------------------------- API REQUESTS ----------------------------


@app.route("/")
def index():
    return profile()
    return render_template('index.html')


@app.route('/search/')
def search():
    try:
        search_type = request.args['search_type']
        name = request.args['name']
        return make_search(search_type, name)
    except:
        return render_template('search.html')


@app.route('/search/<search_type>/<name>')
def search_item(search_type, name):
    return make_search(search_type, name)


def make_search(search_type, name):
    if search_type not in ['artist', 'album', 'playlist', 'track']:
        return render_template('index.html')

    data = spotify.search(search_type, name)
    api_url = data[search_type + 's']['href']
    items = data[search_type + 's']['items']

    return render_template('search.html',
                           name=name,
                           results=items,
                           api_url=api_url,
                           search_type=search_type)


@app.route('/artist/<id>')
def artist(id):
    artist = spotify.get_artist(id)

    if artist['images']:
        image_url = artist['images'][0]['url']
    else:
        image_url = 'http://bit.ly/2nXRRfX'

    tracksdata = spotify.get_artist_top_tracks(id)
    tracks = tracksdata['tracks']

    related = spotify.get_related_artists(id)
    related = related['artists']

    return render_template('artist.html',
                           artist=artist,
                           related_artists=related,
                           image_url=image_url,
                           tracks=tracks)


@app.route('/profile')
def profile():
    if 'auth_header' in session:
        auth_header = session['auth_header']
        # get profile data
        
        tracks_data = spotify.get_tracks("37i9dQZF1DX0XUsuxWHRQd", auth_header)
        # print(tracks_data)
        print('How its Going')

        profile_data = spotify.get_users_profile(auth_header)

        # get user playlist data
        playlist_data = spotify.get_users_playlists(auth_header)
        # get user recently played tracks
        recently_played = spotify.get_users_recently_played(auth_header)

        #get particular playlist details
        get_playlist_details = spotify.get_playlist_details(auth_header,'37i9dQZF1DX0XUsuxWHRQd') 
        # return get_playlist_details
        
        if valid_token(recently_played):
            return render_template("profile.html",
                               user=profile_data,
                               playlists=playlist_data["items"],
                               recently_played=recently_played["items"])

    return render_template('profile.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/featured_playlists')
def featured_playlists():
    if 'auth_header' in session:
        auth_header = session['auth_header']
        hot = spotify.get_featured_playlists(auth_header)
        if valid_token(hot):
            return render_template('featured_playlists.html', hot=hot)

    return render_template('profile.html')

@app.route("/add_playlist_data")
def add_playlist_data():
    if 'auth_header' in session:
        auth_header = session['auth_header']
        return auth_header
        connection = db_connection()
        cursor = connection.cursor()
        cursor.execute("""SELECT name,playlist_id, id, today_followers,yesterday_followers FROM playlists""")
        rows = cursor.fetchall()
        for row in rows:
            playlist_id = row['playlist_id']
            id_playlist = row['id']
            today_followers = row['today_followers']
            yesterday_followers = row['yesterday_followers']

            get_playlist_details = spotify.get_playlist_details(auth_header, playlist_id)
            total_followers      = get_playlist_details['followers']['total']
            name                 = get_playlist_details['name']

            if today_followers == 0:
                yesterday_followers = total_followers

            if total_followers > today_followers:
                yesterday_followers = today_followers
            else:
                total_followers = today_followers
            #insert playlist data
            cursor.execute("UPDATE playlists SET name = ? , today_followers = ? , yesterday_followers = ?  WHERE playlist_id = ?",
                 (name, total_followers, yesterday_followers , playlist_id))
            connection.commit()
            #insert tracks data      
            items = get_playlist_details['tracks']['items']
            cursor.execute("DELETE FROM tracks where playlist_id = ?", [id_playlist] )
            connection.commit()
            for item in items:  
                if item['track'] is not None:
                    track_id   = item['track']['id']
                    tname      = item['track']['name']
                    popularity = item['track']['popularity']
                    added_at   = item['added_at']   
                    cursor.execute("INSERT INTO tracks(track_id, playlist_id ,name , popularity, added_at)  VALUES (?,?,?,?,?)", 
                            [track_id,id_playlist,tname,popularity,added_at])
                    connection.commit()
        return 'inserted';

@app.route("/add_tracks_data")
def add_tracks_data():
    if 'auth_header' in session:
        auth_header = checkToken()
        connection = db_connection()
        cursor = connection.cursor()
        cursor.execute("""SELECT playlist_id, id FROM playlists""")
        rows = cursor.fetchall()
        for row in rows:
            playlist_id = row['playlist_id']
            id_playlist = row['id']
            get_playlist_details = spotify.get_playlist_details(auth_header, playlist_id)
            total_followers      = get_playlist_details['followers']['total']
            name                 = get_playlist_details['name']
            cursor.execute("UPDATE playlists SET name = ? , followers = ? WHERE playlist_id = ?", (name, total_followers,playlist_id))  
            items = get_playlist_details['tracks']['items']
            cursor.execute("DELETE FROM tracks where playlist_id = ?", (id_playlist) )
            connection.commit()
            for item in items:  
                if item['track'] is not None:
                    track_id   = item['track']['id']
                    tname      = item['track']['name']
                    popularity = item['track']['popularity']
                    added_at   = item['added_at']   
                    cursor.execute("INSERT INTO tracks(track_id, playlist_id ,name , popularity, added_at)  VALUES (?,?,?,?,?)", 
                            [track_id,id_playlist,tname,popularity,added_at])      
        connection.commit()
        return 'inserted'
    else:
        return 'Auth Error'

def checkToken():
    if 'expiry_datetime' in session:
        expiry_datetime  = session['expiry_datetime']
        current_datetime = datetime.datetime.now()
        if expiry_datetime <= current_datetime:
            auth_header = spotify.refreshAuth()  
        return auth_header      
    else:
        auth_header = session['auth_header']
        return auth_header 

if __name__ == "__main__":
    app.run(debug=True, port=spotify.PORT)
