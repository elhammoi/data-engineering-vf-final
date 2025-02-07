from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Connexion à MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client["nba_stats"]

@app.route('/')
def index():
    """ Page d'accueil avec liste des équipes """
    teams = db["new_nba_leaders"].distinct("team")  # Liste unique des équipes
    return render_template('index.html', teams=teams)

@app.route('/team/<team_name>')
def team(team_name):
    """ Affiche les stats des joueurs d'une équipe """
    leaders_data = list(db["new_nba_leaders"].find({"team": team_name}))
    shooters_data = list(db["new_nba_shooters"].find({"team": team_name}))
    return render_template('team.html', team_name=team_name, leaders_data=leaders_data, shooters_data=shooters_data)

@app.route('/player/<player_name>')
def player(player_name):
    """ Affiche les stats détaillées d'un joueur """
    leader_stats = db["new_nba_leaders"].find_one({"player_name": player_name})
    shooter_stats = db["new_nba_shooters"].find_one({"name": player_name})

    return render_template('player.html', player_name=player_name, leader_stats=leader_stats, shooter_stats=shooter_stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)