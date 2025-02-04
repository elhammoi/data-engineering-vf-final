from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Connexion à MongoDB
client = MongoClient("mongodb://mongodb:27017/")
db = client["nba_database"]
collection = db["nba_stats"]

@app.route('/')
def home():
    # Récupérer toutes les données de MongoDB
    data = list(collection.find({}, {"_id": 0}))  # On exclut le champ `_id`
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
