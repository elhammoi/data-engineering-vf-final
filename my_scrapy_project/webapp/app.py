import dash
from dash import html
from pymongo import MongoClient

# Connexion à la base "nba_stats"
client = MongoClient("mongodb://mongo:27017/")
db = client["nba_stats"]  # <-- base renommée en "nba_stats"

# Lecture des collections
leaders_data = list(db["nba_leaders"].find({}))
shooters_data = list(db["nba_shooters"].find({}))

# Construction de 2 tableaux HTML
def create_leaders_table(data):
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Category"),
            html.Th("Player"),
            html.Th("Team"),
            html.Th("Value"),
        ])),
        html.Tbody([
            html.Tr([
                html.Td(doc.get("category", "N/A")),
                html.Td(doc.get("player_name", "N/A")),
                html.Td(doc.get("team", "N/A")),
                html.Td(doc.get("value", "N/A"))
            ]) for doc in data
        ])
    ], style={'border': '1px solid black'})

def create_shooters_table(data):
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Rank"),
            html.Th("Name"),
            html.Th("Team"),
            html.Th("Points"),
        ])),
        html.Tbody([
            html.Tr([
                html.Td(doc.get("rank", "N/A")),
                html.Td(doc.get("name", "N/A")),
                html.Td(doc.get("team", "N/A")),
                html.Td(doc.get("points", "N/A"))
            ]) for doc in data
        ])
    ], style={'border': '1px solid black'})

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("NBA Stats"),
    html.H2("Leaders"),
    create_leaders_table(leaders_data),
    html.H2("Shooters"),
    create_shooters_table(shooters_data),
])

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
