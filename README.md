# Spotify Playlists Ranking

## Overview
This is a App for calculating the Promotion Playlists Ranking based upon the tracks on their list makes to the targeted List "RapCaviar" playlist. Ranking is calculated numbers of tracks makes to the RapCaviar and the particular playlist followers.

Percentage for number of tracks makes to "RapCaviar" and their percentage of followers with respect to the highest number of tracks made to "RapCaviar" and highest percetage. Summing up their percentage and calculating with respect to the 100% , promotion playlist is ranked. For those playlist from whom the trck is not yet made to "RapCaviar", their ranking is calculated based on the followers following after the ranking of playlist from whom the tracks made to the "RapCaviar".

 We have used Flask for the web view as we need to show the ranking on the page.

## Run it

1. Clone project and Open Command Line in the Project directory and run followings commands:

```
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
flask created_db
flask add_playlists
python app.py
```

1. For adding tables to the database "flask created_db" , "flask add_playlists" to add playlist Ids to table for fecthing data.
2. python app.py to run the application.
3. CLick on the Login Tab to get access to the account.
4. For pulling playlist tracks data for calculation hit http://127.0.0.1:8081/add_playlist_data in the browser.
5. For Ranking Calculation hit http://127.0.0.1:8081/promotion_ranking  in the browser.
6. For viewing Ranking you can check here: http://127.0.0.1:8081/ranking in the browser.




