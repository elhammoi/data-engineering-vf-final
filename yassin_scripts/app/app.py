from flask import Flask, render_template
from pymongo import MongoClient
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from pandas.plotting import table

matplotlib.use('Agg')  # Utilise un backend non interactif

app = Flask(__name__)

def get_data_from_mongo():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["nba_stats"]
    collection = db["leaders"]
    return list(collection.find())

def get_shooters_from_mongo():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["nba_stats"]
    collection = db["shooters"]
    return list(collection.find().sort("rank", 1))  # Top 10 shooters



@app.route('/')
def home():
    data = get_data_from_mongo()
    shooters_data = get_shooters_from_mongo()

    create_visualization(data)  # Crée des graphiques à partir des données
    create_table_image(data)   # Crée l'image du tableau
    create_shooters_table_image(shooters_data)  # Crée l'image du tableau pour shooters

    return render_template("index.html", image_url="static/nba_leaders_visual.png", table_url="static/nba_table.png",shooters_table_url="static/nba_shooters_table.png")

def create_visualization(data):
    categories = [d["category"] for d in data]
    values = [float(d["value"]) for d in data]

    plt.figure(figsize=(10, 6))
    plt.barh(categories, values, color='orange')
    plt.xlabel('Stats')
    plt.ylabel('Category')
    plt.title(' ')
    plt.savefig("static/nba_leaders_visual.png")
    plt.close()  # Ferme la figure pour libérer la mémoire

def create_table_image(data):
    # Convertir les données en DataFrame Pandas
    df = pd.DataFrame(data)

    # Créer une figure Matplotlib
    fig, ax = plt.subplots(figsize=(10, 5 * 0.6))  # Ajuster la taille en fonction des données
    ax.axis('off')  # Cacher les axes

    # Ajouter le tableau à la figure
    table_data = table(ax, df, loc='center', colWidths=[0.125] * len(df.columns))
    table_data.auto_set_font_size(True)
    table_data.set_fontsize(10)
    table_data.scale(2, 1.2)  # Ajuster la taille du tableau

    # Sauvegarder l'image
    plt.savefig("static/nba_table.png")
    plt.close()

def create_shooters_table_image(shooters_data):
    # Convertir les données des shooters en DataFrame Pandas
    df = pd.DataFrame(shooters_data)

    # Créer une figure Matplotlib
    fig, ax = plt.subplots(figsize=(15, 5))  # Ajuster la taille en fonction des données
    ax.axis('off')  # Cacher les axes

    # Ajouter le tableau à la figure
    table_data = table(ax, df, loc='center', colWidths=[0.08] * len(df.columns))
    table_data.auto_set_font_size(True)
    table_data.set_fontsize(10)
    table_data.scale(2, 1.4)  # Ajuster la taille du tableau

    # Sauvegarder l'image
    plt.savefig("static/nba_shooters_table.png")
    plt.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
