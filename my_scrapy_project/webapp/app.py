from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connexion à MongoDB (vérifiez que l'URL est correcte pour votre environnement)
client = MongoClient("mongodb://mongo:27017/")
db = client["nba_stats"]

@app.context_processor
def inject_now():
    return {'current_year': datetime.utcnow().year}

def remap_totals(doc):
    """
    Remappe les champs d'un document de la collection nba_totals pour corriger le décalage.
    Mapping (après correction) :
      - "Player": Nom du joueur (issu de "Rk")
      - "Age": Âge (issu de "Player")
      - "Team": Équipe (issu de "Age")
      - "Pos": Position (issu de "Team")
      - "G": Matchs joués (issu de "Pos")
      - "GS": Matchs démarrés (issu de "G")
      - "MP": Minutes jouées (issu de "GS")
      - "FG": Field Goals réalisés (issu de "MP")
      - "FGA": Tentatives FG (issu de "FG")
      - "FG%": Pourcentage FG (issu de "FGA")
      - "3P": 3P réalisés (issu de "FG%")
      - "3PA": Tentatives 3P (issu de "3P")
      - "3P%": Pourcentage 3P (issu de "3PA")
      - "2P": 2P réalisés (issu de "3P%")
      - "2PA": Tentatives 2P (issu de "2P")
      - "2P%": Pourcentage 2P (issu de "2PA")
      - "eFG%": Pourcentage FG ajusté (issu de "2P%")
      - "FT": FTs réalisés (issu de "eFG%")
      - "FTA": Tentatives FT (issu de "FT")
      - "FT%": Pourcentage FT (issu de "FTA")
      - "ORB": Rebonds offensifs (issu de "FT%")
      - "DRB": Rebonds défensifs (issu de "ORB")
      - "TRB": Rebonds totaux (issu de "DRB")
      - "AST": Passes décisives (issu de "TRB")
      - "STL": Interceptions (issu de "AST")
      - "BLK": Contres (issu de "STL")
      - "TOV": Ballons perdus (issu de "BLK")
      - "PF": Fautes personnelles (issu de "TOV")
      - "PTS": Points (issu de "PF")
      - "Trp-Dbl": Triple-doubles (issu de "PTS")
      - "Awards": Awards (issu de "Trp-Dbl")
    """
    remapped = {
       "Player": doc.get("Rk", ""),
       "Age": doc.get("Player", ""),
       "Team": doc.get("Age", ""),
       "Pos": doc.get("Team", ""),
       "G": doc.get("Pos", ""),
       "GS": doc.get("G", ""),
       "MP": doc.get("GS", ""),
       "FG": doc.get("MP", ""),
       "FGA": doc.get("FG", ""),
       "FG%": doc.get("FGA", ""),
       "3P": doc.get("FG%", ""),
       "3PA": doc.get("3P", ""),
       "3P%": doc.get("3PA", ""),
       "2P": doc.get("3P%", ""),
       "2PA": doc.get("2P", ""),
       "2P%": doc.get("2PA", ""),
       "eFG%": doc.get("2P%", ""),
       "FT": doc.get("eFG%", ""),
       "FTA": doc.get("FT", ""),
       "FT%": doc.get("FTA", ""),
       "ORB": doc.get("FT%", ""),
       "DRB": doc.get("ORB", ""),
       "TRB": doc.get("DRB", ""),
       "AST": doc.get("TRB", ""),
       "STL": doc.get("AST", ""),
       "BLK": doc.get("STL", ""),
       "TOV": doc.get("BLK", ""),
       "PF": doc.get("TOV", ""),
       "PTS": doc.get("PF", ""),
       "Trp-Dbl": doc.get("PTS", ""),
       "Awards": doc.get("Trp-Dbl", "")
    }
    return remapped

# --- Routes ---

@app.route('/')
def index():
    """
    Page d'accueil : affiche la liste de toutes les équipes issues de nba_totals.
    Utilise le champ "Age" (brut) qui correspond à l'équipe.
    Exclut les valeurs indésirables.
    """
    raw_teams = db["nba_totals"].distinct("Age")
    teams = sorted([t for t in raw_teams if t not in [".360", "2TM", "3TM"]])
    return render_template('index.html', teams=teams)

@app.route('/team/<team_name>')
def team(team_name):
    """
    Affiche la liste des joueurs de l'équipe sélectionnée, avec filtrage par position.
    Le filtre par âge a été retiré.
    Pour filtrer par position, on utilise le champ brut "Team" (qui correspond à la position).
    Après remappage, on utilise "Player" pour le nom, "Age" pour l'âge, "Team" pour l'équipe et "Pos" pour la position.
    """
    selected_position = request.args.get('position')
    query = {"Age": team_name}  # "Age" brut contient l'équipe
    if selected_position:
        query["Team"] = selected_position  # "Team" brut contient la position
    raw_players = list(db["nba_totals"].find(query))
    players = [remap_totals(doc) for doc in raw_players]
    # Pour alimenter le filtre, on extrait les positions disponibles dans cette équipe
    positions = sorted(list(db["nba_totals"].distinct("Team", query)))
    return render_template('team.html', team_name=team_name, positions=positions,
                           selected_position=selected_position, players=players)

@app.route('/player/<player_name>')
def player(player_name):
    """
    Affiche les statistiques détaillées d'un joueur.
    Le nom du joueur est stocké dans le champ "Rk" (dans les données brutes), qui devient "Player" après remappage.
    """
    raw_stats = db["nba_totals"].find_one({"Rk": player_name})
    stats = remap_totals(raw_stats) if raw_stats else None
    return render_template('player.html', player_name=player_name, stats=stats)

@app.route('/top_performers', methods=['GET'])
def top_performers():
    """
    Affiche le classement des 10 meilleurs joueurs selon un critère (par défaut "PTS").
    Permet de filtrer par équipe et par position.
    Pour filtrer par équipe, on utilise le champ brut "Age".
    Pour filtrer par position, on utilise le champ brut "Team".
    Les documents sont regroupés par joueur pour ne pas afficher des doublons.
    """
    # Récupération des filtres et du critère
    criterion = request.args.get('criterion', 'PTS')
    team_filter = request.args.get('team', '')
    position_filter = request.args.get('position', '')
    
    # Construction de la requête
    query = {}
    if team_filter:
        query["Age"] = team_filter
    if position_filter:
        query["Team"] = position_filter
    
    raw_players = list(db["nba_totals"].find(query))
    # Appliquer le remappage pour corriger le décalage des champs
    players = [remap_totals(doc) for doc in raw_players]
    
    # Regrouper les joueurs par leur nom et conserver la meilleure valeur du critère pour chacun
    grouped = {}
    for p in players:
        name = p.get("Player")
        if not name:
            continue
        try:
            val = float(p.get(criterion, 0) or 0)
        except Exception:
            val = 0.0
        if name in grouped:
            try:
                current_val = float(grouped[name].get(criterion, 0) or 0)
            except Exception:
                current_val = 0.0
            if val > current_val:
                grouped[name] = p
        else:
            grouped[name] = p

    unique_players = list(grouped.values())
    
    # Trier les joueurs uniques par le critère choisi (décroissant)
    try:
        players_sorted = sorted(unique_players, key=lambda p: float(p.get(criterion, 0) or 0), reverse=True)
    except Exception:
        players_sorted = unique_players

    top10 = players_sorted[:10]

    # Pour alimenter les filtres dans le template, extraire les valeurs distinctes (brutes)
    teams = sorted(list(db["nba_totals"].distinct("Age")))
    positions = sorted(list(db["nba_totals"].distinct("Team")))
    
    return render_template('top_performers.html', criterion=criterion, players=top10,
                           team_filter=team_filter, position_filter=position_filter,
                           teams=teams, positions=positions)


@app.route('/stats')
def stats():
    """
    Page des statistiques globales : affiche les listes de positions et d'équipes disponibles.
    Utilise le champ brut "Team" pour les positions et "Age" pour les équipes.
    """
    positions = sorted(list(db["nba_totals"].distinct("Team")))
    teams = sorted(list(db["nba_totals"].distinct("Age")))
    return render_template('stats.html', positions=positions, teams=teams)

@app.route('/dashboard/')
def dashboard():
    """Redirige vers /stats."""
    return redirect(url_for('stats'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050, debug=True)
