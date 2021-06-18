from flask import Flask, request, redirect, g, render_template, session
import spotify
import json

import sqlite3
from os import path, getcwd
import re
import os
import sys

app = Flask(__name__)
app.secret_key = 'eLUbsC%e)wKw"T.NC5=P?#AG?tJ_rW'


def db_connection():
    database = path.join(getcwd(), 'pythonsqlite.db')
    # if not path.exists(database):
    #     print('Database file does not exists please check')
    #     exit()
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection


connection = db_connection()
cursor = connection.cursor()


@app.cli.command("create_db")
def create_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id integer PRIMARY KEY,
            playlist_id text NOT NULL,
            name text  NULL,
            today_followers BIGINT DEFAULT 0,
            yesterday_followers BIGINT DEFAULT 0,
            created_at timestamp DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamp DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id integer PRIMARY KEY,
            track_id integer NOT NULL,
            playlist_id text NOT NULL,
            name text NOT NULL,
            popularity BIGINT NOT NULL,
            added_at text NOT NULL,
            created_at timestamp DEFAULT CURRENT_TIMESTAMP,
            updated_at timestamp DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (playlist_id) REFERENCES playlists (id)
        );
    """)
    connection.commit()
    print('Created the Tables')


@app.cli.command("add_playlists")
def add_playlists():
    playlists = [
        "37i9dQZF1DX0XUsuxWHRQd",
        "37i9dQZF1DX4SrOBCjlfVi",
        "37i9dQZF1DWW4igXXl2Qkp",
        "6oZhNW8o5ru7mb4RFkWn0M",
        "6hWMmrVlMTvME8u0KchOpa",
        "6hWMmrVlMTvME8u0KchOpa",
        "6e8MhEouOuoBRYnV9GuGtK",
        "5L3vZ9scrlV9DAcDEagI4c",
        "0UHup1TpaqtEUD3k8H6LG5"
    ]
    for playlist in playlists:
        cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", [playlist])
    connection.commit()
    print("Added playlist entries")


@app.route("/")
def index():
    if 'auth_header' in session:
        auth_header = session['auth_header']
        profile_data = spotify.get_users_profile(auth_header)
        if recently_played is not None and not 'error' in recently_played:
            return render_template("index.html", user=profile_data)
    return render_template('index.html')


@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)


@app.route("/callback/")
def callback():
    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header
    return redirect('/')


def valid_token(resp):
    return resp is not None and not 'error' in resp


@app.route("/add_playlist_data")
def add_playlist_data():
    if 'auth_header' in session:
        auth_header = session['auth_header']
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
            total_followers = get_playlist_details['followers']['total']
            name = get_playlist_details['name']

            if today_followers == 0:
                yesterday_followers = total_followers

            if total_followers > today_followers:
                yesterday_followers = today_followers
            else:
                total_followers = today_followers
            # insert playlist data
            cursor.execute(
                "UPDATE playlists SET name = ? , today_followers = ? , yesterday_followers = ?  WHERE playlist_id = ?",
                (name, total_followers, yesterday_followers, playlist_id))
            connection.commit()
            # insert tracks data
            items = get_playlist_details['tracks']['items']
            cursor.execute("DELETE FROM tracks where playlist_id = ?", [id_playlist])
            connection.commit()
            for item in items:
                if item['track'] is not None:
                    track_id = item['track']['id']
                    tname = item['track']['name']
                    popularity = item['track']['popularity']
                    added_at = item['added_at']
                    cursor.execute(
                        "INSERT INTO tracks(track_id, playlist_id ,name , popularity, added_at)  VALUES (?,?,?,?,?)",
                        [track_id, id_playlist, tname, popularity, added_at])
                    connection.commit()
        return 'inserted';


if __name__ == "__main__":
    app.run(debug=True, port=spotify.PORT)
