import sqlite3
from os import path,getcwd
import re
import os
import sys

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


def create_tables():
    sql_create_playlist_table = """ CREATE TABLE IF NOT EXISTS playlists (
                                            id integer PRIMARY KEY,
                                            playlist_id text NOT NULL,
                                            name text  NULL,
                                            today_followers BIGINT DEFAULT 0,
                                            yesterday_followers BIGINT DEFAULT 0,
                                            created_at timestamp DEFAULT CURRENT_TIMESTAMP,
                                            updated_at timestamp DEFAULT CURRENT_TIMESTAMP
                                        ); """

    sql_create_tracks_table = """CREATE TABLE IF NOT EXISTS tracks (
                                    id integer PRIMARY KEY,
                                    track_id integer NOT NULL,
                                    playlist_id text NOT NULL,
                                    name text NOT NULL,
                                    popularity BIGINT NOT NULL,
                                    added_at text NOT NULL,
                                    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
                                    updated_at timestamp DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (playlist_id) REFERENCES playlists (id)
                                );"""

    data = [ ('37i9dQZF1DX0XUsuxWHRQd'), ('37i9dQZF1DX4SrOBCjlfVi') , ('37i9dQZF1DWW4igXXl2Qkp') ,
            (''), ('4EtswXAGuGuUQcW9ctRour'), ('6hWMmrVlMTvME8u0KchOpa'), ('6hWMmrVlMTvME8u0KchOpa'),
            ('6e8MhEouOuoBRYnV9GuGtK'),('5L3vZ9scrlV9DAcDEagI4c'), ('0UHup1TpaqtEUD3k8H6LG5')
    ]
    connection.execute(sql_create_playlist_table)
    connection.execute(sql_create_tracks_table)
    # connection.execute("INSERT INTO playlists(playlist_id) values (?)", data)
    cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", ['37i9dQZF1DX0XUsuxWHRQd'])
    cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", ['37i9dQZF1DX4SrOBCjlfVi'])
    cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", ['37i9dQZF1DWW4igXXl2Qkp'])

    cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", ['6oZhNW8o5ru7mb4RFkWn0M'])
    cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", ['6hWMmrVlMTvME8u0KchOpa'])
    cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", ['6hWMmrVlMTvME8u0KchOpa'])

    cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", ['6e8MhEouOuoBRYnV9GuGtK'])
    cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", ['5L3vZ9scrlV9DAcDEagI4c'])
    cursor.execute("INSERT INTO playlists(playlist_id)  VALUES (?)", ['0UHup1TpaqtEUD3k8H6LG5'])

    connection.commit()

if __name__ == '__main__':
    create_tables()



