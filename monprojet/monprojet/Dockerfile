# Base image
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Commande pour lancer Flask
CMD ["python", "app.py"]
