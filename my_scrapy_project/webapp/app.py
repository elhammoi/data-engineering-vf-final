from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Connexion à MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client["nba_stats"]

@app.route('/')
def index():
    """ Page d'accueil avec liste des équipes """
    teams = db["new_nba_leaders"].distinct("team")
    return render_template('index.html', teams=teams)

@app.route('/team/<team_name>')
def team(team_name):
    """ Affiche les joueurs de l'équipe et permet de filtrer par catégorie """
    categories = db["new_nba_leaders"].distinct("category")
    selected_category = request.args.get('category')

    # Si une catégorie est sélectionnée, filtrer les joueurs
    if selected_category:
        players_data = list(db["new_nba_leaders"].find({"team": team_name, "category": selected_category}))
    else:
        players_data = list(db["new_nba_leaders"].find({"team": team_name}))

    return render_template('team.html', team_name=team_name, categories=categories,
                           selected_category=selected_category, players_data=players_data)

@app.route('/player/<player_name>')
def player(player_name):
    """ Affiche les statistiques d'un joueur """
    leader_stats = db["new_nba_leaders"].find_one({"player_name": player_name})
    shooter_stats = db["new_nba_shooters"].find_one({"name": player_name})

    return render_template('player.html', player_name=player_name, leader_stats=leader_stats, shooter_stats=shooter_stats)

@app.route('/top_performers', methods=['GET'])
def top_performers():
    """ Classement des 10 meilleurs joueurs par catégorie """
    categories = db["new_nba_leaders"].distinct("category")
    selected_category = request.args.get('category', default=categories[0] if categories else None)

    if selected_category:
        # Récupérer tous les joueurs triés par valeur
        players_cursor = db["new_nba_leaders"].find({"category": selected_category}).sort("value", -1)
        
        # Créer un classement des 10 meilleurs joueurs
        top_players = []
        player_names_seen = set()

        for player in players_cursor:
            name = player["player_name"]
            if name not in player_names_seen:
                top_players.append(player)
                player_names_seen.add(name)
            
            if len(top_players) >= 10:  # Stopper après 10 joueurs uniques
                break
    else:
        top_players = []

    return render_template('top_performers.html', categories=categories, selected_category=selected_category, players=top_players)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050, debug=True)
