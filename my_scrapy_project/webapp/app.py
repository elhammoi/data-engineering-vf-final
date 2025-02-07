from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def index():
    client = MongoClient("mongodb://mongo:27017/")
    db = client["nba_stats"]

    # Récupération des collections
    leaders_data = list(db["new_nba_leaders"].find())
    shooters_data = list(db["new_nba_shooters"].find())

    client.close()

    return render_template('index.html', leaders_data=leaders_data, shooters_data=shooters_data)

@app.route('/team', methods=['GET'])
def team():
    team_name = request.args.get('team')
    client = MongoClient("mongodb://mongo:27017/")
    db = client["nba_stats"]

    # Filtrer les données par équipe
    leaders_data = list(db["new_nba_leaders"].find({"team": team_name}))
    shooters_data = list(db["new_nba_shooters"].find({"team": team_name}))

    client.close()

    return render_template('team.html', team_name=team_name, leaders_data=leaders_data, shooters_data=shooters_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True)