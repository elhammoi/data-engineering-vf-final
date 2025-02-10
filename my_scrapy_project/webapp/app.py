from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connexion à MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client["nba_stats"]

@app.context_processor
def inject_now():
    return {'current_year': datetime.utcnow().year}

@app.route('/')
def index():
    """Page d'accueil avec la liste des équipes (issus des anciennes et nouvelles données)."""
    teams_new = set(db["new_nba_leaders"].distinct("team"))
    teams_old = set(db["leader"].distinct("team"))
    teams = list(teams_new.union(teams_old))
    return render_template('index.html', teams=teams)

@app.route('/team/<team_name>')
def team(team_name):
    """
    Affiche les joueurs d'une équipe avec la possibilité de filtrer par catégorie.
    Combine les données des collections anciennes (leader) et nouvelles (new_nba_leaders).
    """
    categories_new = set(db["new_nba_leaders"].distinct("category"))
    categories_old = set(db["leader"].distinct("category"))
    categories = list(categories_new.union(categories_old))
    
    selected_category = request.args.get('category')
    if selected_category:
        players_new = list(db["new_nba_leaders"].find({"team": team_name, "category": selected_category}))
        players_old = list(db["leader"].find({"team": team_name, "category": selected_category}))
    else:
        players_new = list(db["new_nba_leaders"].find({"team": team_name}))
        players_old = list(db["leader"].find({"team": team_name}))
        
    # Combine les listes (vous pouvez ensuite traiter les doublons si besoin)
    players_data = players_new + players_old
    return render_template('team.html', team_name=team_name, categories=categories,
                           selected_category=selected_category, players_data=players_data)

@app.route('/player/<player_name>')
def player(player_name):
    """
    Affiche les statistiques d'un joueur en combinant les données des collections :
      - leader et new_nba_leaders (pour les statistiques générales)
      - shooters et new_nba_shooters (pour les statistiques de tir)
    """
    new_leader_stats = db["new_nba_leaders"].find_one({"player_name": player_name})
    old_leader_stats = db["leader"].find_one({"player_name": player_name})
    new_shooter_stats = db["new_nba_shooters"].find_one({"name": player_name})
    old_shooter_stats = db["shooters"].find_one({"name": player_name})
    
    return render_template('player.html', player_name=player_name,
                           new_leader_stats=new_leader_stats,
                           old_leader_stats=old_leader_stats,
                           new_shooter_stats=new_shooter_stats,
                           old_shooter_stats=old_shooter_stats)

@app.route('/top_performers', methods=['GET'])
def top_performers():
    """
    Classement des 10 meilleurs joueurs par catégorie.
    Combine les données de new_nba_leaders et leader pour générer un classement.
    On suppose que le champ 'value' contient la statistique utilisée pour le classement.
    """
    categories_new = set(db["new_nba_leaders"].distinct("category"))
    categories_old = set(db["leader"].distinct("category"))
    categories = list(categories_new.union(categories_old))
    
    selected_category = request.args.get('category', default=categories[0] if categories else None)
    if selected_category:
        players_new = list(db["new_nba_leaders"].find({"category": selected_category}))
        players_old = list(db["leader"].find({"category": selected_category}))
        all_players = players_new + players_old
        # Tri des joueurs par la valeur (convertie en float si possible)
        all_players_sorted = sorted(
            all_players,
            key=lambda p: float(p.get("value", 0) or 0),
            reverse=True
        )
        top_players = []
        player_names_seen = set()
        for player in all_players_sorted:
            # Essayer d'obtenir le nom du joueur (champ 'player_name' ou 'name')
            name = player.get("player_name") or player.get("name")
            if name and name not in player_names_seen:
                top_players.append(player)
                player_names_seen.add(name)
            if len(top_players) >= 10:
                break
    else:
        top_players = []
    return render_template('top_performers.html', categories=categories,
                           selected_category=selected_category, players=top_players)

@app.route('/stats')
def stats():
    """
    Page des statistiques globales.
    Combine les catégories et équipes provenant des collections leader et new_nba_leaders.
    """
    categories_new = set(db["new_nba_leaders"].distinct("category"))
    categories_old = set(db["leader"].distinct("category"))
    categories = list(categories_new.union(categories_old))
    
    teams_new = set(db["new_nba_leaders"].distinct("team"))
    teams_old = set(db["leader"].distinct("team"))
    teams = list(teams_new.union(teams_old))
    
    return render_template('stats.html', categories=categories, teams=teams)

@app.route('/dashboard/')
def dashboard():
    """Redirige /dashboard/ vers /stats."""
    return redirect(url_for('stats'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050, debug=True)
